import tkinter as tk


def show_toast(title, message, timeout=2000):
    ret = ["TIMEOUT"]
    root = tk.Tk()
    root.config(background="black")
    root.attributes("-topmost", True)
    # root.wm_attributes("-transparentcolor", "black")
    root.wm_overrideredirect(True)
    w, h = (300, 120)
    root.geometry("{}x{}+{}+{}".format(w, h, 1920 - 10 - w, 1080 - 50 - h))

    def onclick(evt):
        if evt.x < 150:
            ret[0] = "SHOW"
        else:
            ret[0] = "IGNORE"
        root.destroy()

    root.bind("<Button-1>", onclick)

    tk.Label(text=title, font=("SimHei", 18), fg="white", background="black").pack(
        expand=True
    )
    tk.Label(text=message, font=("SimHei", 16), fg="white", background="black").pack(
        expand=True
    )
    tk.Label(
        text="显示        忽略", font=("SimHei", 14), fg="white", background="black"
    ).pack(expand=True)
    root.after(timeout, root.destroy)

    root.mainloop()
    return ret[0]
