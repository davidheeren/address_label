#!/usr/bin/env -S uv run --script

import customtkinter as ctk
import argparse
from main import get_args, run
from pathlib import Path
import json

CONFIG_PATH = Path(__file__).parent / "config.json"


def args_or_default(args: argparse.Namespace) -> argparse.Namespace:
    default_args = get_args(True)
    if args is None:
        return default_args
    merged_vars = {**vars(default_args), **vars(args)}
    return argparse.Namespace(**merged_vars)


def get_and_load_config() -> argparse.Namespace:
    path = Path(CONFIG_PATH)
    args = None
    # if path.is_file():
    if path.is_file():
        with open(CONFIG_PATH, 'r') as f:
            try:
                data = json.load(f)
            except Exception:
                # not valid json
                data = {}
            args = argparse.Namespace(**data)
    return args_or_default(args)


def save_config(args: argparse.Namespace):
    with open(CONFIG_PATH, 'w') as f:
        json.dump(vars(args), f, indent=4)


# TODO: refactor to not one giant function
#       have better names like run and state
# NOTE: this is my using this library or any python gui lol

def main():
    run_gui()


def run_gui():
    ctk.set_appearance_mode("dark")
    ctk.set_widget_scaling(1.25)
    # ctk.set_default_color_theme("blue")
    app = ctk.CTk()
    app.title("Address Label Generator")
    app.geometry("800x800")

    args = get_and_load_config()

    input_var = ctk.StringVar(value=args.input)
    output_var = ctk.StringVar(value=args.output)
    filter_var = ctk.StringVar(value=args.filter)
    bias_var = ctk.StringVar(value=args.bias)
    ret_var = ctk.BooleanVar(value=args.ret)
    test_var = ctk.BooleanVar(value=args.test)
    launch_var = ctk.BooleanVar(value=args.launch)
    tooltip_var = ctk.StringVar(value="")

    def reset_options():
        default_args = get_args(True)
        input_var.set(default_args.input)
        output_var.set(default_args.output)
        filter_var.set(default_args.filter)
        bias_var.set(default_args.bias)
        ret_var.set(default_args.ret)
        test_var.set(default_args.test)
        launch_var.set(default_args.launch)

    def update_input_var():
        dir_path = Path(args.input).parent
        if dir_path == Path("."):
            dir_path = Path.home()
        path = ctk.filedialog.askopenfilename(
            title="Select a File",
            filetypes=[("Data files", "*.csv *.xlsx"), ("All files", "*.*")],
            # need starting /
            initialdir="/" + str(dir_path)
        )
        if not path:
            return
        input_var.set(path)

    def update_output_var():
        dir_path = Path(args.output).parent
        if dir_path == Path("."):
            dir_path = Path.home()
        path = ctk.filedialog.asksaveasfilename(
            title="Select a File",
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
            initialdir="/" + str(dir_path)
        )
        if not path:
            return
        output_var.set(path)

    def save_state():
        save_config(get_state_args())

    def run_state():
        try:
            run(get_state_args())
        except Exception as e:
            tooltip_var.set(e)
            print(e)
        save_state()

    def get_state_args() -> argparse.Namespace:
        return argparse.Namespace(
            input=input_var.get(),
            output=output_var.get(),
            filter=filter_var.get(),
            bias=int(bias_var.get()),
            ret=ret_var.get(),
            test=test_var.get(),
            launch=launch_var.get(),
        )

    def on_frame_enter(text: str):
        tooltip_var.set(text)

    def on_frame_leave(event):
        tooltip_var.set("")

    def validate_integer(new_text: str) -> bool:
        return new_text == "" or new_text.isdigit()

    vint_cmd = (app.register(validate_integer), '%P')

    OUTER_PADX = 20
    OUTER_PADY = 10
    INNER_PADX = 5
    INNER_PADY = 5
    MIN_FRAME_SIZE = 500

    # --- Input Frame ---
    input_frame = ctk.CTkFrame(app)
    input_frame.grid(row=0, column=0, padx=OUTER_PADX, pady=OUTER_PADY, sticky="w")
    input_frame.grid_columnconfigure(0, weight=1, minsize=MIN_FRAME_SIZE)
    input_frame.bind("<Leave>", on_frame_leave)
    input_frame.bind("<Enter>", lambda e: on_frame_enter("<Input> An Excel or csv file that holds the address data"))

    input_header = ctk.CTkLabel(input_frame, text="Input")
    input_header.grid(row=0, column=0, columnspan=1, padx=INNER_PADX, pady=INNER_PADY, sticky="w")
    input_widget = ctk.CTkLabel(input_frame, textvariable=input_var)
    input_widget.grid(row=1, column=0, padx=INNER_PADX, pady=INNER_PADY, sticky="w")
    input_button = ctk.CTkButton(input_frame, text="Choose...", command=update_input_var, width=75)
    input_button.grid(row=1, column=1, padx=INNER_PADX, pady=INNER_PADY, sticky="e")

    # --- Output Frame ---
    output_frame = ctk.CTkFrame(app)
    output_frame.grid(row=1, column=0, padx=OUTER_PADX, pady=OUTER_PADY, sticky="w")
    output_frame.grid_columnconfigure(0, weight=1, minsize=MIN_FRAME_SIZE)
    output_frame.bind("<Leave>", on_frame_leave)
    output_frame.bind("<Enter>", lambda e: tooltip_var.set("<Output> The path of the pdf that will be created"))

    output_header = ctk.CTkLabel(output_frame, text="Output")
    output_header.grid(row=0, column=0, columnspan=1, padx=INNER_PADX, pady=INNER_PADY, sticky="w")
    output_widget = ctk.CTkLabel(output_frame, textvariable=output_var)
    output_widget.grid(row=1, column=0, padx=INNER_PADX, pady=INNER_PADY, sticky="w")
    output_button = ctk.CTkButton(output_frame, text="Choose...", command=update_output_var, width=75)
    output_button.grid(row=1, column=1, padx=INNER_PADX, pady=INNER_PADY, sticky="e")

    # --- Filter Frame ---
    filter_frame = ctk.CTkFrame(app)
    filter_frame.grid(row=2, column=0, padx=OUTER_PADX, pady=OUTER_PADY, sticky="w")
    filter_frame.grid_columnconfigure(0, weight=1, minsize=MIN_FRAME_SIZE)
    filter_frame.bind("<Leave>", on_frame_leave)
    filter_frame.bind("<Enter>", lambda e: tooltip_var.set(
        """<Filter> Chose which rows from the data to include by order
* -> all rows
3 -> single row index
4-9 -> range of row indices
mary jane -> match rows by name. all words in the filter must be included in the row to match
! -> removes the filter instead of add
Ex: '*, !5-20, !john, 15' -> adds all rows, removes range 5-10, removes all john rows, then adds row 15"""))

    filter_header = ctk.CTkLabel(filter_frame, text="Filter")
    filter_header.grid(row=0, column=0, padx=INNER_PADX, pady=INNER_PADY, sticky="w")
    filter_widget = ctk.CTkEntry(filter_frame, textvariable=filter_var)
    filter_widget.grid(row=1, column=0, padx=INNER_PADX, pady=INNER_PADY, sticky="ew")

    # --- Bias Frame ---
    bias_frame = ctk.CTkFrame(app)
    bias_frame.grid(row=3, column=0, padx=OUTER_PADX, pady=OUTER_PADY, sticky="w")
    bias_frame.grid_columnconfigure(0, weight=1, minsize=MIN_FRAME_SIZE)
    bias_frame.bind("<Leave>", on_frame_leave)
    bias_frame.bind("<Enter>", lambda e: tooltip_var.set("<Bias> Number of labels to skip before printing. This is for partially used label papers"))

    bias_header = ctk.CTkLabel(bias_frame, text="Bias")
    bias_header.grid(row=0, column=0, padx=INNER_PADX, pady=INNER_PADY, sticky="w")
    bias_widget = ctk.CTkEntry(bias_frame, textvariable=bias_var, validate="key", validatecommand=vint_cmd)
    bias_widget.grid(row=1, column=0, padx=INNER_PADX, pady=INNER_PADY, sticky="w")

    # --- Ret Frame ---
    ret_frame = ctk.CTkFrame(app)
    ret_frame.grid(row=4, column=0, padx=OUTER_PADX, pady=OUTER_PADY, sticky="w")
    ret_frame.grid_columnconfigure(0, weight=1, minsize=MIN_FRAME_SIZE)
    ret_frame.bind("<Leave>", on_frame_leave)
    ret_frame.bind("<Enter>", lambda e: tooltip_var.set("<Ret> Prints your address the same number of filtered rows"))

    ret_widget = ctk.CTkCheckBox(ret_frame, text="Ret", variable=ret_var)
    ret_widget.grid(row=1, column=0, padx=INNER_PADX, pady=INNER_PADY, sticky="w")

    # --- Test Frame ---
    test_frame = ctk.CTkFrame(app)
    test_frame.grid(row=5, column=0, padx=OUTER_PADX, pady=OUTER_PADY, sticky="w")
    test_frame.grid_columnconfigure(0, weight=1, minsize=MIN_FRAME_SIZE)
    test_frame.bind("<Leave>", on_frame_leave)
    test_frame.bind("<Enter>", lambda e: tooltip_var.set("<Test> Adds a box line around the labels"))

    test_widget = ctk.CTkCheckBox(test_frame, text="Test", variable=test_var)
    test_widget.grid(row=1, column=0, padx=INNER_PADX, pady=INNER_PADY, sticky="w")

    # --- Launch Frame ---
    launch_frame = ctk.CTkFrame(app)
    launch_frame.grid(row=6, column=0, padx=OUTER_PADX, pady=OUTER_PADY, sticky="w")
    launch_frame.grid_columnconfigure(0, weight=1, minsize=MIN_FRAME_SIZE)
    launch_frame.bind("<Leave>", on_frame_leave)
    launch_frame.bind("<Enter>", lambda e: tooltip_var.set("<Launch> Opens the output pdf in the browser when its created"))

    launch_widget = ctk.CTkCheckBox(launch_frame, text="Launch", variable=launch_var)
    launch_widget.grid(row=1, column=0, padx=INNER_PADX, pady=INNER_PADY, sticky="w")

    # --- Task Frame ---
    task_frame = ctk.CTkFrame(app)
    task_frame.grid(row=7, column=0, padx=OUTER_PADX, pady=OUTER_PADY, sticky="w")
    task_frame.grid_columnconfigure(0, weight=1, minsize=MIN_FRAME_SIZE / 2)
    task_frame.grid_columnconfigure(1, weight=1, minsize=MIN_FRAME_SIZE / 2)
    # task_frame.grid_columnconfigure(0, weight=1)

    run_button = ctk.CTkButton(task_frame, text="Run", command=run_state)
    run_button.grid(row=1, column=0, padx=INNER_PADX, pady=INNER_PADY)

    reset_button = ctk.CTkButton(task_frame, text="Reset Options", command=reset_options)
    reset_button.grid(row=1, column=1, padx=INNER_PADX, pady=INNER_PADY)

    # --- Tooltip Frame ---
    tooltip_frame = ctk.CTkFrame(app)
    tooltip_frame.grid(row="8", column=0, padx=OUTER_PADX, pady=OUTER_PADY, sticky="w")
    tooltip_frame.grid_columnconfigure(0, weight=1, minsize=MIN_FRAME_SIZE)

    tooltip_widget = ctk.CTkLabel(tooltip_frame, textvariable=tooltip_var, justify="left")
    tooltip_widget.grid(row=1, column=0, padx=INNER_PADX, pady=INNER_PADY, sticky="w")

    app.mainloop()
    save_state()


if __name__ == "__main__":
    main()
