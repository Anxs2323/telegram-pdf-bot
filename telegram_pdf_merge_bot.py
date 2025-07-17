import os
from telegram import Update, Document
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from PyPDF2 import PdfMerger

TOKEN = "7784674088:AAESaz8pWgK4CpfnnUf0SAG7IztaAM5-zUw"

pdf_storage = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Send me 2 or more PDF files, then type /merge to combine them!")

async def handle_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    file: Document = update.message.document

    if not file.file_name.endswith(".pdf"):
        await update.message.reply_text("⚠️ Please only send PDF files.")
        return

    file_path = f"{user_id}_{file.file_name}"
    pdf_file = await file.get_file()
    await pdf_file.download_to_drive(file_path)

    if user_id not in pdf_storage:
        pdf_storage[user_id] = []

    pdf_storage[user_id].append(file_path)
    await update.message.reply_text(f"✅ Saved: {file.file_name}")

async def merge(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in pdf_storage or len(pdf_storage[user_id]) < 2:
        await update.message.reply_text("📄 You need to send at least 2 PDFs before using /merge.")
        return

    merger = PdfMerger()
    for pdf in pdf_storage[user_id]:
        merger.append(pdf)

    output_filename = f"{user_id}_merged.pdf"
    merger.write(output_filename)
    merger.close()

    await update.message.reply_document(document=open(output_filename, 'rb'))
    await update.message.reply_text("🎉 Done! Here is your merged PDF.")

    for file in pdf_storage[user_id]:
        os.remove(file)
    os.remove(output_filename)
    pdf_storage[user_id] = []

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("merge", merge))
app.add_handler(MessageHandler(filters.Document.PDF, handle_pdf))

if __name__ == "__main__":
    print("🤖 Bot is running...")
    app.run_polling()
