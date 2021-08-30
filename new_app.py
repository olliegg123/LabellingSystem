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
import shelve
from simple_zpl2 import ZPLDocument, Code128_Barcode
from simple_zpl2 import NetworkPrinter

app = Flask(__name__)
d = shelve.open("shelve", writeback=True)
if "OrderNo" in d:
    print("OrderNo exists")
    flag = "OrderNo" in d
    print(flag)
    pass
else:
    print("OrderNo doesn't exist, setting it.")
    d['OrderNo'] = 0
orderNo = d['OrderNo']+1
prn = NetworkPrinter('10.10.10.80')

print(orderNo)

googleSheet = <URL FOR SHEET>
def start():
    global df
    print(datetime.datetime.now())
    if os.path.exists("products.csv"):
        os.remove("products.csv")
        print("File existed, deleting and creating new one.")
    else:
        print("The file does not exist, creating one.") 

    sheets = Sheets.from_files('~/client_secrets.json', '~/storage.json')
    s = sheets.get(googleSheet)
    s.to_csv(make_filename="products.csv")
    df = pd.read_csv("products.csv")
    df['ID'] = np.arange(len(df))

    if os.path.exists("./templates/index3.html"):
        os.remove("./templates/index3.html")
        print("File existed, deleting and creating new one.")
    else:
        print("The file does not exist, creating one.") 


    html = """<html>
        <meta http-equiv="Content-Type" content="text/html; charset="UTF-8">
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
        flavour = re.sub(r'[^A-Za-z0-9\&\xE9 ]+', '', flavour)
        image = "http://cdn.shopify.com/s/files/1/0361/8917/5940/products/Chocolate2stooduplr_large.jpg?v=1585475036"
        buttonName = str(re.sub(r'\W+', '', flavour)+"Button")
        #print(df.loc[df['ID'] == x, 'Flavour'].item())
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
    global orderNo
    d["OrderNo"] = orderNo
    orderNo = orderNo+1
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
        y = 50
        flavour = df.loc[df['ID'] == id, 'Flavour'].item()
        allergens = df.loc[df['ID'] == id, 'Allergens'].item()
        ingredients = df.loc[df['ID'] == id, 'Ingredients'].item()
        #print(f'Ingredient length: {len(ingredients)}')
        #print(f'Flavour length: {len(flavour)}')
        #print(f'Allergen length: {len(allergens)}')
        orderNo_string = str(orderNo)
        fullOrderNo = orderNo_string.zfill(5)

        zdoc = ZPLDocument()
        zdoc.add_zpl_raw('^CI28')
        zdoc.add_zpl_raw('''^XA^FO600,35^GFA,3740,3740,22,,::::::::::::::::::::::::M01IFE,M03KF,M03KFC,M03LF,M03LFC,:M03LFE,M03MF,M03MF8,:M03MFC,::M03MFE,:M03IF1IFE,M03FFE07FFE,::::M03FFE0IFE,M03IF1IFE,M03MFC,::M03MF8,:M03MF,:M03MF8,M03MFC,::M03MFE,M03IF0IFE,M03FFE07FFE,::::M03IF0IFE,M03IF3IFE,M03MFE,:M03MFC,::M03MF8,:M03MF,M03LFE,:M03LF8,M03LF,M03KFC,M03KF,,:::Q03E,P07IFL01JFC,O01JFCK01KFC,O03JFEK01KFE,O0LF8J01LF8,N01LFCJ01LFC,N03LFEJ01MF,:N07MFJ01MF8,:N0NFJ01MFC,N0NF8I01MFC,N0NF8I01MFE,M01NF8I01MFE,M01IFC1IF8I01MFE,M01IF81IFCI01MFE,M01IF80IFCI01IF07IF,M01IF80IF8I01IF07IF,M01IF81IF8I01IF03IF,M01IFC1IF8I01IF03IF,N0IFE3IF8I01IF03IF,N0NFJ01IF07FFE,N0NFJ01IF0IFE,N07LFEJ01MFE,:N03LFC0E001MFC,N03LF81F001MFC,N01LF03F801MFC,N01KFE07FC01MF8,N01KFC0FFE01MF8,N01KF81IF01MF8,N03KF83IF81MFC,N07KFC7IFC1MFC,N0LFCJFC1MFE,M01QF81MFE,M03PFE01IF9IFE,M07PFC01IF07FFE,M07PF801IF03FFE01JF8,M07PF801IF03IF03JFC,M07IF3LF001IF03IF03JFC,M0IFE0KFC001IF03IF03JFC,M0IFC07JF8001IF07IF03JFC,M0IFC07JFI01IF0IFE03JFC,M0IFE07JFI01MFE03JFC,:M0JF0KF8001MFE03JFC,M0PFC001MFE03JFC,M0PFE001MFC03JFC,M07PF001MFC03JFC,M07PF801MFC03JFC,M07PFC01MF803JFC,M03PFE01MF003JFC,M03QF01MF003JFC,M01LFDJF81LFE003JFC,N0LF8JFC1LFC003JFC,N03JFE07IFC1KFEI03JFC,N01JF803IFC1KFCI03JFC,O07FFEI0IFC1JFCJ03JFC,P07CX01JF8,,::::::::::::::::::::::::^FS''')

        zdoc.add_font(font_name="R", character_height = 9, character_width=9)
        zdoc.add_field_origin(x_pos=35, y_pos=y)
        zdoc.add_field_block(width=150, max_lines=2)
        zdoc.add_field_data("Flavour:")

        zdoc.add_font(font_name="T", character_height = 9, character_width=9)
        zdoc.add_field_origin(x_pos=210, y_pos=y)
        zdoc.add_field_block(width=410, max_lines=40)
        zdoc.add_field_data(flavour)

        if len(flavour) >= 23:
            y=y+100
        else:
            y=y+50

        zdoc.add_font(font_name="R", character_height = 9, character_width=9)
        zdoc.add_field_origin(x_pos=35, y_pos=y)
        zdoc.add_field_block(width=200, max_lines=1)
        zdoc.add_field_data("Date Packed:")

        zdoc.add_zpl_raw('^A0N,31,31')
        zdoc.add_field_origin(x_pos=210, y_pos=y)
        zdoc.add_field_block(width=600, max_lines=40)
        zdoc.add_field_data(date_time)

        y=y+50

        zdoc.add_font(font_name="R", character_height = 9, character_width=9)
        zdoc.add_field_origin(x_pos=35, y_pos=y)
        zdoc.add_field_block(width=200, max_lines=1)
        zdoc.add_field_data("Best Before:")

        zdoc.add_zpl_raw('^A0N,31,31')
        zdoc.add_field_origin(x_pos=210, y_pos=y)
        zdoc.add_field_block(width=600, max_lines=40)
        zdoc.add_field_data(date_future)

        y=y+50

        zdoc.add_font(font_name="R", character_height = 9, character_width=9)
        zdoc.add_field_origin(x_pos=35, y_pos=y)
        zdoc.add_field_block(width=200, max_lines=1)
        zdoc.add_field_data("Order ID:")

        zdoc.add_zpl_raw('^A0N,31,31')
        zdoc.add_field_origin(x_pos=210, y_pos=y)
        zdoc.add_field_block(width=600, max_lines=40)
        zdoc.add_field_data(fullOrderNo)

        y=y+50

        zdoc.add_font(font_name="R", character_height = 9, character_width=9)
        zdoc.add_field_origin(x_pos=35, y_pos=y)
        zdoc.add_field_block(width=150, max_lines=1)
        zdoc.add_field_data("Allergens:")

        zdoc.add_zpl_raw('^A0N,31,31')
        zdoc.add_field_origin(x_pos=210, y_pos=y)
        zdoc.add_field_block(width=550, max_lines=40)
        zdoc.add_field_data(allergens)

        if len(allergens) > 42:
            y=y+20

        y=y+70
        #print(y)

        if y+len(ingredients) >1250:
            font='Q'
        else:
            font='F'

        zdoc.add_font(font_name="R", character_height = 9, character_width=9)
        zdoc.add_field_origin(x_pos=35, y_pos=y)
        zdoc.add_field_block(width=150, max_lines=1)
        zdoc.add_field_data("Ingredients:")

        zdoc.add_font(font_name=font, character_height = 31, character_width=31)
        zdoc.add_field_origin(x_pos=210, y_pos=y)
        zdoc.add_field_block(width=575, max_lines=40)
        zdoc.add_field_data(ingredients)

        zdoc.add_font(font_name="R", character_height = 9, character_width=9)
        zdoc.add_field_origin(x_pos=35, y_pos=1120)
        zdoc.add_field_block(width=1500, max_lines=1)
        zdoc.add_field_data("Produced by Brown & Blond.")

        zdoc.add_font(font_name="R", character_height = 9, character_width=9)
        zdoc.add_field_origin(x_pos=35, y_pos=1160)
        zdoc.add_field_block(width=1500, max_lines=1)
        zdoc.add_field_data("Unit 7, Wortley Business Park, Leeds, LS12 4WE")

        #print(zdoc.zpl_text)
        #prn.print_zpl(zdoc)

        #print(flavour)
        #print(allergens)
        #print(ingredients)

        message = f"Order No: {fullOrderNo} - Flavour: {flavour} - Time: {now}\n"
        log = open("./log.txt","a")
        print('\n')
        print(message)
        log.write(message)
        log.close()

        return str(id)

if __name__ == "__main__":
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(debug=True, host="0.0.0.0")
    
