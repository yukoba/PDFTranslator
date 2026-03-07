import os
import threading
from tkinter import filedialog, messagebox

import customtkinter as ctk

from src.config_manager import ConfigManager
from src.pdf_processor import PDFProcessor
from src.translator import Translator

ctk.set_appearance_mode("Dark")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")


class PDFTranslatorApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("PDF Translator")
        self.geometry("620x500")

        self.config_manager = ConfigManager()

        self._create_widgets()
        self._load_config()

    def _create_widgets(self):
        # 1. PDF File Selection
        self.file_frame = ctk.CTkFrame(self)
        self.file_frame.pack(pady=10, padx=20, fill="x")

        self.file_label = ctk.CTkLabel(self.file_frame, text="PDF File:")
        self.file_label.pack(side="left", padx=10)

        self.file_path_var = ctk.StringVar()
        self.file_entry = ctk.CTkEntry(
            self.file_frame,
            textvariable=self.file_path_var,
            width=350,
            state="readonly",
        )
        self.file_entry.pack(side="left", padx=10)

        self.browse_btn = ctk.CTkButton(
            self.file_frame, text="Browse", command=self._browse_file, width=80
        )
        self.browse_btn.pack(side="left", padx=10)

        # 2. Language Selection
        self.lang_frame = ctk.CTkFrame(self)
        self.lang_frame.pack(pady=10, padx=20, fill="x")

        self.src_lang_label = ctk.CTkLabel(self.lang_frame, text="Source Language:")
        self.src_lang_label.grid(row=0, column=0, padx=10, pady=5, sticky="e")

        self.src_lang_var = ctk.StringVar(value="English")
        self.src_lang_menu = ctk.CTkOptionMenu(
            self.lang_frame, variable=self.src_lang_var, values=["English", "Japanese"]
        )
        self.src_lang_menu.grid(row=0, column=1, padx=10, pady=5, sticky="w")

        self.tgt_lang_label = ctk.CTkLabel(self.lang_frame, text="Target Language:")
        self.tgt_lang_label.grid(row=0, column=2, padx=10, pady=5, sticky="e")

        self.tgt_lang_var = ctk.StringVar(value="Japanese")
        self.tgt_lang_menu = ctk.CTkOptionMenu(
            self.lang_frame, variable=self.tgt_lang_var, values=["Japanese", "English"]
        )
        self.tgt_lang_menu.grid(row=0, column=3, padx=10, pady=5, sticky="w")

        # 3. Page Range
        self.page_frame = ctk.CTkFrame(self)
        self.page_frame.pack(pady=10, padx=20, fill="x")

        self.page_label = ctk.CTkLabel(self.page_frame, text="Page Range:")
        self.page_label.pack(side="left", padx=10)

        self.start_page_var = ctk.StringVar()
        self.start_page_entry = ctk.CTkEntry(
            self.page_frame,
            textvariable=self.start_page_var,
            width=50,
            placeholder_text="Start",
        )
        self.start_page_entry.pack(side="left", padx=5)

        self.to_label = ctk.CTkLabel(self.page_frame, text="to")
        self.to_label.pack(side="left", padx=5)

        self.end_page_var = ctk.StringVar()
        self.end_page_entry = ctk.CTkEntry(
            self.page_frame,
            textvariable=self.end_page_var,
            width=50,
            placeholder_text="End",
        )
        self.end_page_entry.pack(side="left", padx=5)

        self.page_info_label = ctk.CTkLabel(
            self.page_frame, text="(Leave empty for all pages)", text_color="gray"
        )
        self.page_info_label.pack(side="left", padx=10)

        # 4. LLM Selection & API Key
        self.llm_frame = ctk.CTkFrame(self)
        self.llm_frame.pack(pady=10, padx=20, fill="x")

        self.model_label = ctk.CTkLabel(self.llm_frame, text="LLM Model:")
        self.model_label.grid(row=0, column=0, padx=10, pady=5, sticky="e")

        self.model_var = ctk.StringVar(value="gemini-3-flash-preview")
        self.model_menu = ctk.CTkOptionMenu(
            self.llm_frame,
            variable=self.model_var,
            values=["gemini-3-flash-preview", "gpt-5-mini"],
            command=self._on_model_change,
        )
        self.model_menu.grid(row=0, column=1, padx=10, pady=5, sticky="w")

        self.api_key_label = ctk.CTkLabel(self.llm_frame, text="API Key:")
        self.api_key_label.grid(row=1, column=0, padx=10, pady=5, sticky="e")

        self.api_key_var = ctk.StringVar()
        self.api_key_entry = ctk.CTkEntry(
            self.llm_frame, textvariable=self.api_key_var, width=350, show="*"
        )
        self.api_key_entry.grid(row=1, column=1, padx=10, pady=5, sticky="w")

        # 5. Output Preview
        self.output_frame = ctk.CTkFrame(self)
        self.output_frame.pack(pady=10, padx=20, fill="both", expand=True)

        self.output_label = ctk.CTkLabel(self.output_frame, text="Translation Log:")
        self.output_label.pack(anchor="w", padx=10, pady=5)

        self.output_text = ctk.CTkTextbox(self.output_frame, height=100)
        self.output_text.pack(padx=10, pady=5, fill="both", expand=True)
        self.output_text.configure(state="disabled")

        # 6. Execute Button & Progress
        self.action_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.action_frame.pack(pady=10, padx=20, fill="x")

        self.exec_btn = ctk.CTkButton(
            self.action_frame,
            text="Translate",
            command=self._start_translation,
            height=40,
            font=("Arial", 16, "bold"),
        )
        self.exec_btn.pack(side="left", padx=10)

        self.progress_var = ctk.DoubleVar(value=0.0)
        self.progress_bar = ctk.CTkProgressBar(
            self.action_frame, variable=self.progress_var, width=300
        )
        self.progress_bar.pack(side="left", padx=10, pady=10)

        self.status_var = ctk.StringVar(value="Ready")
        self.status_label = ctk.CTkLabel(
            self.action_frame, textvariable=self.status_var
        )
        self.status_label.pack(side="left", padx=10)

    def _load_config(self):
        self.src_lang_var.set(self.config_manager.get("source_language", "English"))
        self.tgt_lang_var.set(self.config_manager.get("target_language", "Japanese"))

        saved_model = self.config_manager.get("selected_model", "gpt-5-mini")
        self.model_var.set(saved_model)

        self._load_api_key(saved_model)

    def _load_api_key(self, model_name: str):
        api_key = self.config_manager.get_api_key(model_name)
        if api_key:
            self.api_key_var.set(api_key)
        else:
            self.api_key_var.set("")

    def _save_current_config(self):
        self.config_manager.set("source_language", self.src_lang_var.get())
        self.config_manager.set("target_language", self.tgt_lang_var.get())

        current_model = self.model_var.get()
        self.config_manager.set("selected_model", current_model)

        current_key = self.api_key_var.get().strip()
        if current_key:
            self.config_manager.set_api_key(current_model, current_key)

        file_path = self.file_path_var.get()
        if file_path:
            self.config_manager.set("last_opened_folder", os.path.dirname(file_path))

    def _on_model_change(self, new_model: str):
        self._load_api_key(new_model)

    def _browse_file(self):
        initial_dir = self.config_manager.get(
            "last_opened_folder", os.path.expanduser("~")
        )
        file_path = filedialog.askopenfilename(
            initialdir=initial_dir,
            title="Select PDF File",
            filetypes=(("PDF files", "*.pdf"), ("All files", "*.*")),
        )
        if file_path:
            self.file_path_var.set(file_path)

    def _log_message(self, message: str):
        self.output_text.configure(state="normal")
        self.output_text.insert("end", message + "\n")
        self.output_text.see("end")
        self.output_text.configure(state="disabled")

    def _start_translation(self):
        pdf_path = self.file_path_var.get()
        api_key = self.api_key_var.get().strip()
        model_name = self.model_var.get()
        target_lang = self.tgt_lang_var.get()

        if not pdf_path:
            messagebox.showerror("Error", "Please select a PDF file.")
            return

        if not api_key:
            messagebox.showerror("Error", "Please enter an API key.")
            return

        # Save config
        self._save_current_config()

        # Parse pages
        start_p_str = self.start_page_var.get().strip()
        end_p_str = self.end_page_var.get().strip()

        start_page = int(start_p_str) if start_p_str.isdigit() else 1
        end_page = int(end_p_str) if end_p_str.isdigit() else None

        # Output Markdown path
        base_name = os.path.splitext(pdf_path)[0]
        md_path = f"{base_name}.md"

        # Update UI state
        self.exec_btn.configure(state="disabled")
        self.browse_btn.configure(state="disabled")
        self.progress_var.set(0.0)
        self.output_text.configure(state="normal")
        self.output_text.delete("1.0", "end")
        self.output_text.configure(state="disabled")

        self._log_message(f"Starting translation: {os.path.basename(pdf_path)}")
        self._log_message(f"Target: {target_lang} | Model: {model_name}")
        self._log_message(f"Output will be saved to: {md_path}")

        # Start thread
        thread = threading.Thread(
            target=self._translation_worker,
            args=(
                pdf_path,
                md_path,
                model_name,
                api_key,
                target_lang,
                start_page,
                end_page,
            ),
        )
        thread.daemon = True
        thread.start()

    def _translation_worker(
            self, pdf_path, md_path, model_name, api_key, target_lang, start_page, end_page
    ):
        try:
            translator = Translator(model_type=model_name, api_key=api_key)  # type: ignore

            with PDFProcessor(pdf_path) as proc:
                total_pages = proc.get_page_count()
                actual_end_page = (
                    end_page if end_page and end_page <= total_pages else total_pages
                )

                if start_page > actual_end_page or start_page < 1:
                    self.after(
                        0,
                        self._log_message,
                        f"Error: Invalid page range (1 - {total_pages}).",
                    )
                    self.after(0, self._finish_translation)
                    return

                pages_to_process = actual_end_page - start_page + 1
                processed_count = 0
                previous_context = None

                self.after(
                    0, self.status_var.set, f"Processing {pages_to_process} pages..."
                )

                for page_num, image in proc.extract_pages_as_images(
                        start_page, actual_end_page
                ):
                    self.after(0, self._log_message, f"Translating page {page_num}...")

                    try:
                        translated_markdown = translator.translate_page(
                            image,
                            target_language=target_lang,
                            previous_context=previous_context,
                        )

                        # Write to file (Append)
                        with open(md_path, "a", encoding="utf-8") as md_file:
                            md_file.write(f"\n\n<!-- Page {page_num} -->\n\n")
                            md_file.write(translated_markdown)

                        self.after(
                            0,
                            self._log_message,
                            f"✓ Page {page_num} appended to {os.path.basename(md_path)}",
                        )

                        # Extract the last part of the translation for context (e.g., last 200 characters)
                        previous_context = (
                            translated_markdown[-200:]
                            if len(translated_markdown) > 200
                            else translated_markdown
                        )

                    except Exception as e:
                        self.after(
                            0,
                            self._log_message,
                            f"❌ Error on page {page_num}: {str(e)}",
                        )
                        # Decide whether to continue or abort on error

                    processed_count += 1
                    progress = processed_count / pages_to_process
                    self.after(0, self.progress_var.set, progress)
                    self.after(
                        0,
                        self.status_var.set,
                        f"Translating... ({processed_count}/{pages_to_process})",
                    )

            self.after(0, self._log_message, "\n🎉 Translation completed successfully!")
            self.after(0, self.status_var.set, "Completed")

        except Exception as e:
            self.after(0, self._log_message, f"\n❌ Fatal Error: {str(e)}")
            self.after(0, self.status_var.set, "Error")

        finally:
            self.after(0, self._finish_translation)

    def _finish_translation(self):
        self.exec_btn.configure(state="normal")
        self.browse_btn.configure(state="normal")


if __name__ == "__main__":
    app = PDFTranslatorApp()
    app.mainloop()
