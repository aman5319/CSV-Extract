from flask import Flask, request, flash, redirect, render_template, url_for, Markup, send_file
import os, shutil
import pandas as pd
import re
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)

app.secret_key = "dasdsa34542+3432dash13210990 !@#$%^&*("
# the upload path for all the files
UPLOAD_FOLDER = os.getcwd() + "/" + "uploadFolder"
# a list to track all the files loaded in memory
list_of_uploaded_file = []


def clean_upload_folder():
    try:
        shutil.rmtree(UPLOAD_FOLDER + "/")
    except FileNotFoundError as e:
        pass


def make_directory():
    os.mkdir(UPLOAD_FOLDER)


@app.route('/')
def root():
    # clean the upload directory every time user use the website and create a new empty directory
    clean_upload_folder()
    make_directory()
    list_of_uploaded_file.clear()
    return render_template("upload.html")


@app.route("/upload", methods=["POST"])
def upload_csv_file():
    print("root testing" , request.files)
    if request.method == "POST":
        # check wether the request value is 
        print("upload file" , request.files)
        if "file" in request.files:
            # get the multiDict
            print("something")
            upload_file = request.files.getlist("file")
            print("upload file" , request.files)
            for file in upload_file:
                # secure the filename which will only give file name excluding other parameters
                filename = secure_filename(file.filename)
                #print(filename , "  " , dir(file.stream))
                # get the file path
                path = os.path.join(UPLOAD_FOLDER, filename)
                file.save(path)

                # this condition check is if csv file is valid after saving the file it tries to read it
                # if valid csv file the only add to  list_of_uploaded_file
                try:
                    pd.read_csv(path)
                    list_of_uploaded_file.append(filename)
                except:
                    os.remove(path)
            # redirect to view csv the condition on filename is when single invalid file is added
            #  when multiple csv file is added and few are invalid then it is automatically skipped and valid one is added to list
            return redirect(url_for("view_csv", filename=list_of_uploaded_file[0] if len(
                list_of_uploaded_file) > 0 else invalid()))
        else:
            flash("Select CSV files then upload")
            return redirect(url_for("root"))


def invalid():
    flash("Invalid CSV files ")
    return redirect(url_for("root"))


@app.route("/viewCSV/<string:filename>", methods=["GET"])
def view_csv(filename):
    if len(list_of_uploaded_file) > 0:
        print(list_of_uploaded_file)
        df = pd.read_csv(os.path.join(UPLOAD_FOLDER, filename))
        # to show the checkbox inside cell
        checkbox = '{value}<br/><input type="checkbox" name="{value}" value="{value}">'
        # list(df) gives all columns
        columns = [checkbox.format(value=col) for col in list(df)]
        # change the column
        df.columns = columns
        s = df.to_html(index=False)
        # the < and > symbols are converted to &lt; and &gt; symbols after it is converted to html
        # convert it again to original form
        s = re.sub("&lt;", "<", re.sub("&gt;", ">", s))
        # Markup(s) to execute HTML code in jinja
        return render_template("viewDataFrame.html", dataframe=Markup(s), filelist=list_of_uploaded_file,
                               currentfile=filename)
    else:
        flash("Select CSV files then upload")
        return redirect(url_for("root"))


@app.route("/downloadcsv/<string:filename>", methods=["POST"])
def download(filename):
    if request.method == "POST":
        column = list(request.form.keys())
        if len(column) > 0:
            dataframe = pd.read_csv(os.path.join(UPLOAD_FOLDER, filename))
            # slices the dataframe and takes only the desired columns the extraction process
            dataframe = dataframe[column]
            # get a valid file name
            file_to_write = filename.replace(".csv", "") + "_" + datetime.now().strftime("%c").replace(" ",
                                                                                                       "_") + ".csv"
            path = os.path.join(UPLOAD_FOLDER, file_to_write)
            # save to csv file and send for download
            dataframe.to_csv(path, index=False)
            return send_file(path, mimetype="text/csv", attachment_filename=file_to_write, as_attachment=True)
        else:
            flash("First Select something")
            return redirect(url_for('view_csv', filename=filename))


if __name__ == '__main__':
    app.run(debug=True)
