from flask import Flask, jsonify, request, render_template, send_from_directory
from flask_mysqldb import MySQL
from werkzeug.utils import secure_filename
import os
import openai

app = Flask(__name__)
mysql = MySQL(app)

app.config['UPLOAD_FOLDER'] = ''
app.config['MYSQL_HOST'] = ''
app.config['MYSQL_USER'] = ''   
app.config['MYSQL_PASSWORD'] = '' 
app.config['MYSQL_DB'] = ''

openai.api_key = 'YOUR_OPENAI_API_KEY'

# home route
@app.route('/')
def home():
    return render_template('mainform.html')

@app.route('/data', methods=['GET', 'POST'])
def dataku():
    if request.method == 'GET':
        x = mysql.connection.cursor()
        jmlData = x.execute('select * from mytable')
        print(jmlData)
        if jmlData > 0:
            data = x.fetchall()
            print(data)

            allData = []
            for i in range(len(data)):
                id = data[i][0]
                name = data[i][1]
                age = data[i][2]
                link = data[i][3]
                dataDict = {
                    "id": id,
                    "name": name,
                    "age": age,
                    "link": link
                }
                allData.append(dataDict)
            return jsonify(allData)
        else:
            return jsonify({'status': 'No data available'})
    else:
        name = request.form['name']
        age = request.form['age']
        data = request.files['photo']

        namefile = secure_filename(data.filename)
        data.save(os.path.join(app.config['UPLOAD_FOLDER'], namefile))
        link = 'http://127.0.0.1:5000/upload/' + namefile

        x = mysql.connection.cursor()
        x.execute(
            'insert into mytable (name, age, link) values (%s, %s, %s)',
            (name, age, link)
        )
        mysql.connection.commit()
        
        # Use ChatGPT API to generate a response
        prompt = f"My name is {name}, and I am {age} years old. Here is a picture of me: {link}."
        response = openai.Completion.create(
            model="text-davinci-002",
            prompt=prompt,
            max_tokens=50
        )
        chat_response = response.choices[0].text

        return render_template('successpage.html', name=name, age=age, link=link, chat_response=chat_response)

@app.route('/upload/<namefile>')
def upload(namefile):
    return send_from_directory('./storage', namefile)

# activate server
if __name__ == '__main__':
    app.run(debug=True)
