#!/usr/bin/env -S uv run --script

import customtkinter as ctk
import argparse
from main import get_args
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


def main():
    # args = get_and_load_config()
    # print(vars(args))
    # save_config(args)
    run_gui()


def run_gui():
    ctk.set_appearance_mode("dark")
    ctk.set_widget_scaling(1.5)
    # ctk.set_default_color_theme("blue")
    app = ctk.CTk()
    app.title("Address Label Generator")
    app.geometry("500x400")
    app.grid_columnconfigure(0, weight=1)

    args = get_and_load_config()

    input_var = ctk.StringVar(value=args.input)
    output_var = ctk.StringVar(value=args.output)
    filter_var = ctk.StringVar(value=args.filter)
    # bias_var = ctk.StringVar(value=args.bias)
    # return_var = ctk.BooleanVar(value=args.ret)
    # test_var = ctk.BooleanVar(value=args.test)
    # launch_var = ctk.BooleanVar(value=args.launch)

    def update_input_var():
        default = Path(args.input)
        if default.is_file():
            dir_path = default.parent
        else:
            dir_path = Path.home()
        path = ctk.filedialog.askopenfilename(
            title="Select a File",
            filetypes=[("Data files", "*.csv *.xlsx"), ("All files", "*.*")],
            initialdir=dir_path
        )
        if not path:
            return
        print(path)
        input_var.set(path)

    def update_output_var():
        default = Path(args.output)
        if default.is_file():
            dir_path = default.parent
        else:
            dir_path = Path.home()
        path = ctk.filedialog.asksaveasfilename(
            title="Select a File",
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
            initialdir=dir_path
        )
        if not path:
            return
        print(path)
        output_var.set(path)

    # --- Input Frame ---
    input_frame = ctk.CTkFrame(app)
    input_frame.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
    input_frame.grid_columnconfigure(0, weight=1)

    input_header = ctk.CTkLabel(input_frame, text="Input (data path)")
    input_header.grid(row=0, column=0, columnspan=2, padx=20, pady=(10, 5), sticky="w")
    input_widget = ctk.CTkLabel(input_frame, textvariable=input_var)
    input_widget.grid(row=1, column=0, padx=20, pady=(5, 10), sticky="ew")
    input_button = ctk.CTkButton(input_frame, text="Choose...", command=update_input_var, width=50)
    input_button.grid(row=1, column=1, padx=(0, 20), pady=(5, 10))

    # --- Output Frame ---
    output_frame = ctk.CTkFrame(app)
    output_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
    output_frame.grid_columnconfigure(0, weight=1)

    output_header = ctk.CTkLabel(output_frame, text="Output (pdf path)")
    output_header.grid(row=0, column=0, columnspan=2, padx=20, pady=(10, 5), sticky="w")
    output_widget = ctk.CTkLabel(output_frame, textvariable=output_var)
    output_widget.grid(row=1, column=0, padx=20, pady=(5, 10), sticky="ew")
    output_button = ctk.CTkButton(output_frame, text="Choose...", command=update_output_var, width=50)
    output_button.grid(row=1, column=1, padx=(0, 20), pady=(5, 10))

    # --- Filter Frame ---
    filter_frame = ctk.CTkFrame(app)
    filter_frame.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
    filter_frame.grid_columnconfigure(0, weight=1)

    filter_header = ctk.CTkLabel(filter_frame, text="Filter (filter data rows)")
    filter_header.grid(row=0, column=0, padx=20, pady=(10, 5), sticky="w")
    filter_widget = ctk.CTkEntry(filter_frame, textvariable=filter_var)
    filter_widget.grid(row=1, column=0, padx=20, pady=(5, 10), sticky="ew")

    app.mainloop()


if __name__ == "__main__":
    main()
