import pandas as pd
import re
import os
from flask import Flask, render_template, request, jsonify
import requests
from datetime import datetime
import datetime
import json
from gsheets import Sheets
import numpy as np

app = Flask(__name__)

Bartender_URL = <INSERT URL>
googleSheet = <INSERT SHEET URL>
def start():
    global df
    if os.path.exists("products.csv"):
        os.remove("products.csv")
    else:
        print("The file does not exist") 

    sheets = Sheets.from_files('~/client_secrets.json', '~/storage.json')
    s = sheets.get(googleSheet)
    s.to_csv(make_filename="products.csv")
    df = pd.read_csv("products.csv")
    df['ID'] = np.arange(len(df))

    if os.path.exists("./templates/index3.html"):
        os.remove("./templates/index3.html")
    else:
        print("The file does not exist") 


    html = """<html>
        <meta http-equiv="Content-Type" content="text/html; charset=ISO-8859-1">
        <head>      
            <link href="http://libs.baidu.com/bootstrap/3.0.3/css/bootstrap.min.css" rel="stylesheet">
            <script src="//ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js"></script>
            <script src="https://libs.baidu.com/bootstrap/3.0.3/js/bootstrap.min.js"></script>
        <style>
    .message-selected {
        filter: brightness(150%);
        color: green;    
    }
        </style>
        </head>
        <body style="display: inline-flex;flex-wrap: wrap;">"""
    for x in range(0, len(df)):
        id = x
        flavour = str(df.loc[df['ID'] == x, 'Flavour'].item())
        flavour = re.sub(r'[^A-Za-z0-9 ]+', '', flavour)
        image = "http://cdn.shopify.com/s/files/1/0361/8917/5940/products/Chocolate2stooduplr_large.jpg?v=1585475036"
        buttonName = str(re.sub(r'\W+', '', flavour)+"Button")
        print(df.loc[df['ID'] == x, 'Flavour'].item())
        html = html+f'''
        <div id="{flavour}" class="button-container" style="margin: 10px; width: 150px; height: 150px; position: relative; text-align: center; color: white;">
            <img style="filter: brightness(75%)" width=150px src="{image}">
            <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); font-family: 'Franklin Gothic Medium', 'Arial Narrow', Arial, sans-serif; font-size:large">{flavour}</div>
        </div>
        <script>
            const {buttonName} = document.getElementById('{flavour}');
            {buttonName}.addEventListener('click', function () {{
                $.ajax({{
                url: '/printLabel',
                data: {{
                    id: "{id}",
                }},
                dataType : 'json'
            }})
            }});
        </script>

        '''
    html=html+"""<div id="reset" class="button-container" style="width: 150px; height: 150px; position: relative; text-align: center; color: white;">
            <img style="filter: brightness(75%)" width=150px src="https://centredexcellence.co.uk/wp-content/uploads/2015/04/bigstock-Reset-Red-Button-5147739.jpg">
            <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); font-family: 'Franklin Gothic Medium', 'Arial Narrow', Arial, sans-serif; font-size:large"></div>
        </div>
        <script>
            const resetButton = document.getElementById('reset');
            resetButton.addEventListener('click', function () {
                $.ajax({
                url: '/printLabel',
                data: {
                    id: "9999",
                },
                dataType : 'json'
        })
        setTimeout(location.reload.bind(location), 4000);
        });
        </script>
        <script> $("div").click(function() {
        $("div").removeClass('message-selected');
        $(this).addClass('message-selected'); 
    });</script></body>
    </html>"""
    file = open("./templates/index3.html","w")
    file.write(html)
    file.close()

start()

@app.route('/')
@app.route('/index.html')
def index():
    return render_template('index3.html')


@app.route('/printLabel')
def add():
    now = datetime.datetime.now()
    future = now + datetime.timedelta(days=10)
    date_time = now.strftime("%Y-%m-%d")
    date_future = future.strftime("%Y-%m-%d")
    id = request.args.get('id', type=int)
    if id == 9999:
        print("reset pressed")
        start()
        return ("reset")
    else:
        flavour = df.loc[df['ID'] == id, 'Flavour'].item()
        allergens = df.loc[df['ID'] == id, 'Allergens'].item()
        ingredients = df.loc[df['ID'] == id, 'Ingredients'].item()
        print(flavour)
        print(allergens)
        print(ingredients)
        headers = {
            "Content-Type": "application/json"
        }
        payload = {
            "Allergens": allergens,
            "Flavour": flavour,
            "Ingredients": ingredients,
            "PackDate": date_time,
            "BBDate": date_future
        }
        print(payload)
        r = requests.post(Bartender_URL, data=json.dumps(payload), headers=headers)
        print("label printed")
        return str(id)

if __name__ == "__main__":
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(debug=True, host="0.0.0.0")
    