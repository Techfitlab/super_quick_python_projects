import base64
import io
import os
import json
import plotly.graph_objs as go
import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import pandas as pd
config = json.loads(open("./config.json").read())
os.environ["DIR"] = config["currentDirectory"]
os.chdir(os.environ["DIR"])
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server
app.title = 'Visualiser'
colors = {
"background": "#ffffff",
"text": "#004687",
"graphBackground": "#EFEFEF"
}

app.layout = html.Div([html.H1('VISUALISER',
                               style={
                                      'textAlign': 'center',
                                      "background": "#EFEFEF"}),
    dcc.Upload(
        id='upload-data',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Upload Files')
        ]),
        style={
            'width': '98%','height': '60px','lineHeight': '60px','borderWidth': '1px','borderStyle': 'dashed',
            'borderRadius': '5px','textAlign': 'center','margin': '10px'
        },
        multiple=True
    ),
    dcc.Graph(id='graph1'),
    dcc.Graph(id='graph2'),
    html.Div(id='table2'),
    html.Div(id='table1')
    ], style={'padding':10})

def parseData(contents, filename):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename: # csv file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')))
        elif 'xls' in filename: # xls file
            df = pd.read_excel(io.BytesIO(decoded))
        elif 'txt' or 'tsv' in filename:
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')), delimiter=r'\s+')
    except Exception as err:
        print(err)
        return html.Div([
            'There was an error processing this file.'
        ])
    
    return df

@app.callback(Output('graph1', 'figure'), [
Input('upload-data', 'contents'),
Input('upload-data', 'filename')
])
def updateGraph1(contents, filename):
    x = []
    y = []
    if contents:
        contents = contents[0]
        filename = filename[0]
        df = parseData(contents, filename)
        x=df.iloc[:,0]
        y=df.iloc[:,1]
    fig = go.Figure(
        data=[
            go.Scatter(
                x=x, 
                y=y, 
                mode='lines+markers',
        marker=dict(
            color='LightSkyBlue',
            size=1,
            line=dict(
                color='DarkSlateGrey',
                width=2
            )
        ),
        showlegend=False)
            ],
        layout=go.Layout(
            title = 'Visualiser Plot 1',
            plot_bgcolor=colors["graphBackground"],
            paper_bgcolor=colors["graphBackground"]
        ))
    return fig

@app.callback(Output('graph2', 'figure'), [
Input('upload-data', 'contents'),
Input('upload-data', 'filename')
])
def updateGraph2(contents, filename):
    z = []
    w = []
    if contents:
        contents = contents[0]
        filename = filename[0]
        df = parseData(contents, filename)
        # Using specific column names
        dff = df.groupby(["type"]).tmax.sum().reset_index()
        z=dff["type"]
        w=dff["tmax"]
    fig = go.Figure()
    fig.add_trace(go.Bar(x=z,
                y=w,
                name='Jurisdiction',
                marker_color='rgb(55, 83, 109)'
                ))
    fig.update_layout(
    title='Visualiser Plot 2',
    xaxis_tickfont_size=9,
    plot_bgcolor=colors["graphBackground"],
    paper_bgcolor=colors["graphBackground"],
    yaxis=dict(
        tickfont_size=12,
    ))
    return fig


@app.callback(Output('table1', 'children'),
          [
Input('upload-data', 'contents'),
Input('upload-data', 'filename')
])
def updateTable1(contents, filename):
    table = html.Div()
    if contents:
        contents = contents[0]
        filename = filename[0]
        df = parseData(contents, filename)
    
        table = html.Div([
            html.H5(filename),
            dash_table.DataTable(
                data=df.to_dict('rows'),
                columns=[{'name': i, 'id': i} for i in df.columns]
            ),
            html.Hr()
        ])

    return table

@app.callback(Output('table2', 'children'),
          [
Input('upload-data', 'contents'),
Input('upload-data', 'filename')
])
def updateTable2(contents, filename):
    table = html.Div()
    if contents:
        contents = contents[0]
        filename = filename[0]
        df = parseData(contents, filename)
        perc =[.20, .40, .60, .80] 
        include =['object', 'float', 'int'] 
        data = df.describe(percentiles = perc, include = include)
        data["summary"] = data.index
        data = data.reset_index()
        data = data[["summary","date","tmax","flag","type"]]
        data = pd.DataFrame(data)
        table = html.Div([
            html.H5(filename),
            dash_table.DataTable(
                data=data.to_dict('rows'),
                columns=[{'name': i, 'id': i} for i in data.columns]
            ),
            html.Hr()
        ])

    return table
if __name__ == '__main__':
    app.run_server(debug=True)