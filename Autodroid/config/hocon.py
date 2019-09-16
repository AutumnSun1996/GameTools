import pyhocon
import yaml
import json
import re
from pyhocon.config_parser import *

from pyparsing import ParseBaseException


class MyConfigParser(ConfigParser):
    """
    Parse HOCON files: https://github.com/typesafehub/config/blob/master/HOCON.md
    """

    @classmethod
    def parse(cls, content, basedir=None, resolve=True, unresolved_value=DEFAULT_SUBSTITUTION):
        """parse a HOCON content

        :param content: HOCON content to parse
        :type content: basestring
        :param resolve: if true, resolve substitutions
        :type resolve: boolean
        :param unresolved_value: assigned value value to unresolved substitution.
        If overriden with a default value, it will replace all unresolved value to the default value.
        If it is set to to pyhocon.STR_SUBSTITUTION then it will replace the value by its substitution expression (e.g., ${x})
        :type unresolved_value: boolean
        :return: a ConfigTree or a list
        """

        unescape_pattern = re.compile(r'\\.')

        def replace_escape_sequence(match):
            value = match.group(0)
            return cls.REPLACEMENTS.get(value, value)

        def norm_string(value):
            return unescape_pattern.sub(replace_escape_sequence, value)

        def unescape_string(tokens):
            return ConfigUnquotedString(norm_string(tokens[0]))

        def parse_multi_string(tokens):
            # remove the first and last 3 "
            return tokens[0][3: -3]

        def convert_number(tokens):
            n = tokens[0]
            try:
                return int(n, 10)
            except ValueError:
                return float(n)

        def convert_period(tokens):

            period_value = int(tokens.value)
            period_identifier = tokens.unit

            period_unit = next((single_unit for single_unit, values
                                in cls.get_supported_period_type_map().items()
                                if period_identifier in values))

            return period(period_value, period_unit)

        # ${path} or ${?path} for optional substitution
        SUBSTITUTION_PATTERN = r"\$\{(?P<optional>\?)?(?P<variable>[^}]+)\}(?P<ws>[ \t]*)"

        def create_substitution(instring, loc, token):
            # remove the ${ and }
            match = re.match(SUBSTITUTION_PATTERN, token[0])
            variable = match.group('variable')
            ws = match.group('ws')
            optional = match.group('optional') == '?'
            substitution = ConfigSubstitution(variable, optional, ws, instring, loc)
            return substitution

        # ${path} or ${?path} for optional substitution
        STRING_PATTERN = '"(?P<value>(?:[^"\\\\]|\\\\.)*)"(?P<ws>[ \t]*)'

        def create_quoted_string(instring, loc, token):
            # remove the ${ and }
            match = re.match(STRING_PATTERN, token[0])
            value = norm_string(match.group('value'))
            ws = match.group('ws')
            return ConfigQuotedString(value, ws, instring, loc)

        def include_config(instring, loc, token):
            url = None
            file = None
            required = False

            if token[0] == 'required':
                required = True
                final_tokens = token[1:]
            else:
                final_tokens = token

            if len(final_tokens) == 1:  # include "test"
                value = final_tokens[0].value if isinstance(final_tokens[0], ConfigQuotedString) else final_tokens[0]
                if value.startswith("http://") or value.startswith("https://") or value.startswith("file://"):
                    url = value
                else:
                    file = value
            elif len(final_tokens) == 2:  # include url("test") or file("test")
                value = final_tokens[1].value if isinstance(token[1], ConfigQuotedString) else final_tokens[1]
                if final_tokens[0] == 'url':
                    url = value
                else:
                    file = value

            if url is not None:
                logger.debug('Loading config from url %s', url)
                obj = MyConfigFactory.parse_URL(
                    url,
                    resolve=False,
                    required=required,
                    unresolved_value=NO_SUBSTITUTION
                )
            elif file is not None:
                path = file if basedir is None else os.path.join(basedir, file)
                logger.debug('Loading config from file %s', path)
                obj = MyConfigFactory.parse_file(
                    path,
                    resolve=False,
                    required=required,
                    unresolved_value=NO_SUBSTITUTION
                )
            else:
                raise ConfigException('No file or URL specified at: {loc}: {instring}', loc=loc, instring=instring)

            return ConfigInclude(obj if isinstance(obj, list) else obj.items())

        @contextlib.contextmanager
        def set_default_white_spaces():
            default = ParserElement.DEFAULT_WHITE_CHARS
            ParserElement.setDefaultWhitespaceChars(' \t')
            yield
            ParserElement.setDefaultWhitespaceChars(default)

        with set_default_white_spaces():
            assign_expr = Forward()
            true_expr = Keyword("true", caseless=True).setParseAction(replaceWith(True))
            false_expr = Keyword("false", caseless=True).setParseAction(replaceWith(False))
            null_expr = Keyword("null", caseless=True).setParseAction(replaceWith(NoneValue()))
            # key = QuotedString('"', escChar='\\', unquoteResults=False) | Word(alphanums + alphas8bit + '._- /')
            # key = QuotedString('"', escChar='\\', unquoteResults=False) | CharsNotIn(" +=:$\\'\"{}")
            key = QuotedString('"', escChar='\\', unquoteResults=False) | Word(alphanums + alphas8bit + '._- /')

            eol = Word('\n\r').suppress()
            eol_comma = Word('\n\r,').suppress()
            comment = (Literal('#') | Literal('//')) - SkipTo(eol | StringEnd())
            comment_eol = Suppress(Optional(eol_comma) + comment)
            comment_no_comma_eol = (comment | eol).suppress()
            number_expr = Regex(r'[+-]?(\d*\.\d+|\d+(\.\d+)?)([eE][+\-]?\d+)?(?=$|[ \t]*([\$\}\],#\n\r]|//))',
                                re.DOTALL).setParseAction(convert_number)

            period_types = itertools.chain.from_iterable(cls.get_supported_period_type_map().values())
            period_expr = Regex(r'(?P<value>\d+)\s*(?P<unit>' + '|'.join(period_types) + ')$'
                                ).setParseAction(convert_period)

            # multi line string using """
            # Using fix described in http://pyparsing.wikispaces.com/share/view/3778969
            multiline_string = Regex('""".*?"*"""', re.DOTALL | re.UNICODE).setParseAction(parse_multi_string)
            # single quoted line string
            quoted_string = Regex(r'"(?:[^"\\\n]|\\.)*"[ \t]*', re.UNICODE).setParseAction(create_quoted_string)
            # unquoted string that takes the rest of the line until an optional comment
            # we support .properties multiline support which is like this:
            # line1  \
            # line2 \
            # so a backslash precedes the \n
            unquoted_string = Regex(r'(?:[^^`+?!@*&"\[\{\s\]\}#,=\$\\]|\\.)+[ \t]*',
                                    re.UNICODE).setParseAction(unescape_string)
            substitution_expr = Regex(r'[ \t]*\$\{[^\}]+\}[ \t]*').setParseAction(create_substitution)
            string_expr = multiline_string | quoted_string | unquoted_string

            value_expr = period_expr | number_expr | true_expr | false_expr | null_expr | string_expr

            include_content = (quoted_string | ((Keyword('url') | Keyword('file')) -
                                                Literal('(').suppress() - quoted_string - Literal(')').suppress()))
            include_expr = (
                Keyword("include", caseless=True).suppress() + (
                    include_content | (
                        Keyword("required") - Literal('(').suppress() - include_content - Literal(')').suppress()
                    )
                )
            ).setParseAction(include_config)

            root_dict_expr = Forward()
            dict_expr = Forward()
            list_expr = Forward()
            multi_value_expr = ZeroOrMore(comment_eol | include_expr | substitution_expr | dict_expr | list_expr | value_expr | (Literal(
                '\\') - eol).suppress())
            # for a dictionary : or = is optional
            # last zeroOrMore is because we can have t = {a:4} {b: 6} {c: 7} which is dictionary concatenation
            inside_dict_expr = ConfigTreeParser(ZeroOrMore(comment_eol | include_expr | assign_expr | eol_comma))
            inside_root_dict_expr = ConfigTreeParser(ZeroOrMore(
                comment_eol | include_expr | assign_expr | eol_comma), root=True)
            dict_expr << Suppress('{') - inside_dict_expr - Suppress('}')
            root_dict_expr << Suppress('{') - inside_root_dict_expr - Suppress('}')
            list_entry = ConcatenatedValueParser(multi_value_expr)
            list_expr << Suppress('[') - ListParser(list_entry - ZeroOrMore(eol_comma - list_entry)) - Suppress(']')

            # special case when we have a value assignment where the string can potentially be the remainder of the line
            assign_expr << Group(
                key - ZeroOrMore(comment_no_comma_eol) - (dict_expr | (Literal('=') | Literal(':') | Literal('+=')) - ZeroOrMore(
                    comment_no_comma_eol) - ConcatenatedValueParser(multi_value_expr))
            )

            # the file can be { ... } where {} can be omitted or []
            config_expr = ZeroOrMore(comment_eol | eol) + (list_expr | root_dict_expr | inside_root_dict_expr) + ZeroOrMore(
                comment_eol | eol_comma)
            config = config_expr.parseString(content, parseAll=True)[0]

            if resolve:
                allow_unresolved = resolve and unresolved_value is not DEFAULT_SUBSTITUTION and unresolved_value is not MANDATORY_SUBSTITUTION
                has_unresolved = cls.resolve_substitutions(config, allow_unresolved)
                if has_unresolved and unresolved_value is MANDATORY_SUBSTITUTION:
                    raise ConfigSubstitutionException(
                        'resolve cannot be set to True and unresolved_value to MANDATORY_SUBSTITUTION')

            if unresolved_value is not NO_SUBSTITUTION and unresolved_value is not DEFAULT_SUBSTITUTION:
                cls.unresolve_substitutions_to_value(config, unresolved_value)
        return config


class MyConfigFactory(ConfigFactory):
    @classmethod
    def parse_file(cls, filename, encoding='utf-8', required=True, resolve=True, unresolved_value=DEFAULT_SUBSTITUTION):
        """Parse file

        :param filename: filename
        :type filename: basestring
        :param encoding: file encoding
        :type encoding: basestring
        :param required: If true, raises an exception if can't load file
        :type required: boolean
        :param resolve: if true, resolve substitutions
        :type resolve: boolean
        :param unresolved_value: assigned value value to unresolved substitution.
        If overriden with a default value, it will replace all unresolved value to the default value.
        If it is set to to pyhocon.STR_SUBSTITUTION then it will replace the value by its substitution expression (e.g., ${x})
        :type unresolved_value: boolean
        :return: Config object
        :type return: Config
        """
        logger.warning('Try to include %s.', filename)
        try:
            with codecs.open(filename, 'r', encoding=encoding) as fd:
                content = fd.read()

            if filename.endswith(".yaml"):
                logger.warning('Try to include %s with yaml loader.', filename)
                import yaml
                d = yaml.safe_load(content)
                return cls.from_dict(d)

            return cls.parse_string(content, os.path.dirname(filename), resolve, unresolved_value)
        except IOError as e:
            if required:
                raise e
            logger.warn('Cannot include file %s. File does not exist or cannot be read.', filename)
            return []

    @classmethod
    def parse_string(cls, content, basedir=None, resolve=True, unresolved_value=DEFAULT_SUBSTITUTION):
        """Parse URL

        :param content: content to parse
        :type content: basestring
        :param resolve: If true, resolve substitutions
        :param resolve: if true, resolve substitutions
        :type resolve: boolean
        :param unresolved_value: assigned value value to unresolved substitution.
        If overriden with a default value, it will replace all unresolved value to the default value.
        If it is set to to pyhocon.STR_SUBSTITUTION then it will replace the value by its substitution expression (e.g., ${x})
        :type unresolved_value: boolean
        :return: Config object
        :type return: Config
        """
        return MyConfigParser().parse(content, basedir, resolve, unresolved_value)


def to_hocon(config, compact=False, indent=2, level=0):
    """Convert HOCON input into a HOCON output

    :return: JSON string representation
    :type return: basestring
    """
    lines = ""
    if isinstance(config, ConfigTree):
        if len(config) == 0:
            lines += '{}'
        else:
            if level > 0:  # don't display { at root level
                lines += '{\n'
            bet_lines = []

            for key, item in config.items():
                if compact:
                    full_key = key
                    while isinstance(item, ConfigTree) and len(item) == 1:
                        key, item = next(iter(item.items()))
                        full_key += '.' + key
                else:
                    full_key = key

                if not re.match(r"^[a-zA-Z0-9._\- /]+$", full_key):
                    full_key = '"{value}"'.format(value=full_key.replace('\n', '\\n').replace('"', '\\"'))
                bet_lines.append('{indent}{key}{assign_sign} {value}'.format(
                    indent=''.rjust(level * indent, ' '),
                    key=full_key,
                    assign_sign='' if isinstance(item, dict) else ' =',
                    value=to_hocon(item, compact, indent, level + 1))
                )
            lines += '\n'.join(bet_lines)

            if level > 0:  # don't display { at root level
                lines += '\n{indent}}}'.format(indent=''.rjust((level - 1) * indent, ' '))
    elif isinstance(config, list):
        if len(config) == 0:
            lines += '[]'
        else:
            simple = True
            for item in config:
                if not isinstance(item, (basestring, int, float, bool)):
                    simple = False
                    break
            if simple:
                cur_line = '['
                items = [to_hocon(item, compact, 0, level + 1) for item in config]
                cur_line += ", ".join(items)
                cur_line += ']'.format(indent=''.rjust((level - 1) * indent, ' '))
                if indent + len(cur_line) > 80:
                    simple = False
                else:
                    lines += cur_line
            if not simple:
                lines += '[\n'
                bet_lines = []
                for item in config:
                    bet_lines.append('{indent}{value}'.format(indent=''.rjust(level * indent, ' '),
                                                              value=to_hocon(item, compact, indent, level + 1)))
                lines += '\n'.join(bet_lines)
                lines += '\n{indent}]'.format(indent=''.rjust((level - 1) * indent, ' '))
    elif isinstance(config, basestring):
        if '\n' in config:
            lines = '"""{value}"""'.format(value=config)  # multilines
        else:
            lines = '"{value}"'.format(value=config.replace('\n', '\\n').replace('"', '\\"'))
    elif isinstance(config, ConfigValues):
        lines = ''.join(to_hocon(o, compact, indent, level) for o in config.tokens)
    elif isinstance(config, ConfigSubstitution):
        lines = '${'
        if config.optional:
            lines += '?'
        lines += config.variable + '}' + config.ws
    elif isinstance(config, ConfigQuotedString):
        if '\n' in config.value:
            lines = '"""{value}"""'.format(value=config.value)  # multilines
        else:
            lines = '"{value}"'.format(value=config.value.replace('\n', '\\n').replace('"', '\\"'))
    elif config is None or isinstance(config, NoneValue):
        lines = 'null'
    elif config is True:
        lines = 'true'
    elif config is False:
        lines = 'false'
    else:
        lines = str(config)
    return lines


def load(path):
    logger.info("Load hocon %s", path)
    tree = MyConfigFactory.parse_file(path)
    return tree

def dump(obj, path):
    text = to_hocon(obj)
    with open(path, "w", -1, "UTF8") as fl:
        fl.write(text)

if __name__ == "__main__":
    import sys
    path = sys.argv[1]
    conf = load(path)
    if path.endswith(".yaml"):
        dump(conf, path.replace(".yaml", ".conf"))
    else:
        print(to_hocon(conf))
