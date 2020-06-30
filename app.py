import datetime

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table as dt
import yaml
from bson.objectid import ObjectId
from dash.dependencies import Input, Output, State
from pymongo import MongoClient

with open('config.yaml', 'r') as ymlfile:
    cfg = yaml.load(ymlfile, Loader=yaml.BaseLoader)

client = MongoClient(host=cfg['server']['host'])
db = client[cfg['server']['db']]

table_header_style = {
    "backgroundColor": "rgb(2,21,70)",
    "color": "white",
    "textAlign": "center",
}


def layout():
    page = html.Div([
        html.Div(
            [
                dcc.Input(id="input-id", type="text", placeholder="", debounce=True),
                html.Button('Trash',
                            id='trash-button',
                            n_clicks=0,
                            style={'float': 'right'}
                            ),
            ],
        ),
        html.Div(
            [
                dt.DataTable(
                    id="data-table",
                    columns=[
                        {
                            "name": "ObjectId",
                            "id": "column-index",
                            "type": "numeric",
                            "selectable": True,
                        },
                        {
                            "name": "Summary",
                            "id": "column-summary",
                            "type": "text",
                            "selectable": True,
                        },
                        {
                            "name": "Datetime",
                            "id": "column-datetime",
                            "type": "datetime",
                            "selectable": False,
                        }
                    ],
                    # fixed_columns={'headers': True, 'data': 1},
                    editable=False,
                    css=[{'selector': 'table', 'rule': 'table-layout: fixed'}],
                    style_header=table_header_style,
                    fixed_columns={"headers": True},
                    # row_deletable=True,
                    # active_cell={"row": 0, "column": 0},
                    # row_selectable="single",  # radio button
                    style_cell={'textAlign': 'left'},
                    style_cell_conditional=[
                        {'if': {'column_id': 'column-index'}, 'width': '12%'},
                        {'if': {'column_id': 'column-summary'}, 'width': '77%'},
                        {'if': {'column_id': 'column-datetime'}, 'width': '11%'},
                    ],
                    style_table={'height': '300px', 'overflowY': 'auto'},
                    selected_cells=[{"row": 0, "column": 0}],
                ),
                html.Div(id='source-container', children=[]),
                dcc.Textarea(
                    id='textarea-summary',
                    value="",
                    style={'width': '100%',
                           'font-size': '15px',
                           'height': 100},
                ),
                html.Button('submit',
                            id='submit-button',
                            n_clicks=0,
                            style={'width': '20%'}
                            ),
                html.I(id='output'),
            ]
        )
    ])
    return page


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.layout = layout


# @app.callback(
#     Output('source-container', 'children'),
#     [Input('input-id', 'value')],
#     [State('source-container', 'children')])
# def update_news(value, children):
#     retrieved_posts = db.posts.find({'category': value})
#     for post in retrieved_posts:
#         for news in post['news']:
#             children.append(html.H6(children=news))
#         return children
#
#     return []
#
#
# @app.callback(
#     Output('textarea-summary', 'value'),
#     [Input('input-id', 'value')])
# def update_news(value):
#     retrieved_posts = db.posts.find({'category': value})
#     for post in retrieved_posts:
#         return post['summary']
#
#     return ""

# @app.callback(
#     Output('data-table', 'data'),
#     [Input('input-id', 'value')])
# def update_table(value):
#     retrieved_posts = db.posts.find({'category': value})
#     records = []
#     for post in retrieved_posts:
#         date_time = datetime.datetime.now()
#         records.append({"column-index": str(post['_id']),
#                         "column-summary": post['summary'],
#                         "column-datetime": date_time.strftime("%m/%d/%Y, %H:%M:%S")})
#     return records
@app.callback(
    [
        Output('data-table', 'data'),
        Output('data-table', 'style_data_conditional')
    ],
    [
        Input('input-id', 'value'),
        Input('input-id', 'n_submit'),
    ])
def update_table(value, n_submit):
    retrieved_posts = db.posts.find({'worker': value})
    records, marked = [], []

    for post in retrieved_posts:
        summary = post.get('summary', post.get('semi-summary')) or post.get('semi-summary')
        update_datetime = post.get('update_datetime', '')
        records.append({"column-index": str(post['_id']),
                        "column-summary": summary,
                        "column-datetime": update_datetime})
        if post['completed']:
            marked.append(str(post['_id']))

    style_data_conditional = [{
        'if': {
            'column_id': 'column-index',
            'filter_query': '{column-index} eq ' + oid,
        },
        'backgroundColor': 'rgb(102, 209, 244)',
        "color": "white",
    } for oid in marked]
    return records, style_data_conditional


@app.callback(
    [
        Output('source-container', 'children'),
        Output('textarea-summary', 'value'),
    ],
    [
        Input('data-table', 'derived_virtual_row_ids'),
        Input('data-table', 'selected_row_ids'),
        Input('data-table', 'active_cell')
    ],
    [
        State('data-table', 'data'),
    ])
def load_news(row_ids, selected_row_ids, active_cell, data):
    # When the table is first rendered, `derived_virtual_data` and
    # `derived_virtual_selected_rows` will be `None`. This is due to an
    # idiosyncracy in Dash (unsupplied properties are always None and Dash
    # calls the dependent callbacks when the component is first rendered).
    # So, if `rows` is `None`, then the component was just rendered
    # and its value will be the same as the component's dataframe.
    # Instead of setting `None` in here, you could also set
    # `derived_virtual_data=df.to_rows('dict')` when you initialize
    # the component.

    # if selected_row_ids:
    #     row_idx = selected_row_ids['column-index']

    if active_cell and data:
        news_collections = []
        object_id = data[active_cell['row']]['column-index']
        retrieved_posts = db.posts.find({"_id": ObjectId(object_id)})
        post = retrieved_posts[0]
        for news in post['sources']:
            news_collections.append(html.P(children=news))
        summary = post.get('summary', post.get('semi-summary')) or post.get('semi-summary')
        # update_datetime = post.get('update_datetime', '')

        return news_collections, summary

    return [], ""


@app.callback(
    # [
    #     Output('output', 'children'),
    #     Output('data-table', 'data'),
    # ],
    Output('output', 'children'),
    [
        Input('submit-button', 'n_clicks'),
        Input('trash-button', 'n_clicks'),
    ],
    [
        State('data-table', 'data'),
        State('data-table', 'active_cell'),
        State('textarea-summary', 'value')
    ]
)
def update_output(btn1, btn2, data, active_cell, value):
    message = ""
    if active_cell:
        changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
        if 'submit-button' in changed_id:
            object_id = data[active_cell['row']]['column-index']
            date_time = datetime.datetime.now()
            db.posts.update_one(
                {"_id": ObjectId(object_id)},
                {"$set": {"summary": value, "completed": True,
                          "update_datetime": date_time.strftime("%m/%d/%Y, %H:%M:%S")}},
                upsert=True
            )
            message = "Updated"
        elif 'trash-button' in changed_id:
            object_id = data[active_cell['row']]['column-index']
            db.posts.delete_one({"_id": ObjectId(object_id)})
            # del data[active_cell['row']]
            message = "Erased"

    return message  #, data if data else []


# @app.callback(
#     Output('output', 'children'),
#     [
#         Input('trash-button', 'n_clicks'),
#     ],
#     [
#         State('data-table', 'data'),
#         State('data-table', 'active_cell'),
#     ]
# )
# def update_output(n_clicks, data, active_cell):
#     if n_clicks > 0 and active_cell:
#         object_id = data[active_cell['row']]['column-index']
#         db.posts.delete_one({"_id": ObjectId(object_id)})
#         return "Erased"


if __name__ == '__main__':
    app.run_server(host="0.0.0.0", port=8899, debug=True)
