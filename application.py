from flask import Flask, render_template, jsonify, request
from utils import get_data_from_pdf

application = Flask(__name__)

@application.route("/", methods=('GET', 'POST'))
def home():
   if request.method == 'POST':
      url = request.form.get("filepath")
      if url:
         data = get_data_from_pdf(url)
         return jsonify({"status": "success", "data": data})
      return jsonify({"status": "fail", "code": "Missing filepath perameter."})
   return render_template("index.html")



@application.route("/rse/pdf-process/api/", methods=('GET', 'POST'))
def pdf_process():
   if request.method == 'POST':
      url = request.form.get("filepath")
      if url:
         data = get_data_from_pdf(url)
         return jsonify({"status": "success", "data": data})
      return jsonify({"status": "fail", "code": "Missing filepath perameter."})
   return jsonify({"status": "fail", "code": "Method not allowed."})


if __name__ == "__main__":
    application.run()