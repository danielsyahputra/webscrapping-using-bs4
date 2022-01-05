from flask import Flask, render_template
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from bs4 import BeautifulSoup 
import requests

#don't change this
matplotlib.use('Agg')
app = Flask(__name__) #do not change this

#insert the scrapping here
url_get = requests.get('https://pusatdata.kontan.co.id/makroekonomi/inflasi')
soup = BeautifulSoup(url_get.content,"html.parser")

#find your right key here
table = soup.find('div', attrs={'class':'baris-scroll'})
rows = table.find_all('div', attrs={'class':'kol-konten3-1'})
row_length = len(rows)

temp = [] #initiating a list 

for i in range(1, row_length):
	# Get period of row-i
	periode = table.findAll('div', attrs={'class': 'kol-konten3-1'})[i].text

	# Get inflation mom of row-i
	inflation_mom = table.findAll('div', attrs={'class': 'kol-konten3-2'})[i].text
	inflation_mom = inflation_mom.strip()

	# Get inflation yoy of row-i
	inflation_yoy = table.findAll('div', attrs={'class': 'kol-konten3-3'})[i].text
	inflation_yoy = inflation_yoy.strip()

	temp.append((periode, inflation_mom, inflation_yoy))

temp = temp[::-1]

#change into dataframe
df = pd.DataFrame(data=temp, columns=['period','inflation_mom','inflation_yoy'])


#insert data wrangling here
df['inflation_mom'] = df['inflation_mom'].str.replace(',', '.').astype('float64')
df['inflation_yoy'] = df['inflation_yoy'].str.replace(',', '.').astype('float64')
df['period'] = df['period'].astype('datetime64')
df = df.set_index('period')


#end of data wranggling 

@app.route("/")
def index(): 
	
	card_data = f'{df["inflation_mom"].mean().round(2)}' #be careful with the " and ' 

	# generate plot
	ax = df.plot(figsize = (20,9)) 
	
	# Rendering plot
	# Do not change this
	figfile = BytesIO()
	plt.savefig(figfile, format='png', transparent=True)
	figfile.seek(0)
	figdata_png = base64.b64encode(figfile.getvalue())
	plot_result = str(figdata_png)[2:-1]

	# render to html
	return render_template('index.html',
		card_data = card_data, 
		plot_result=plot_result
		)


if __name__ == "__main__": 
    app.run(debug=True)