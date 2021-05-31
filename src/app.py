# app.py
# provides the Flask application

from flask import Flask, Response, request
from sqlalchemy import create_engine, Table, MetaData
from sqlalchemy.sql.functions import func
from sqlalchemy.orm import sessionmaker

app = Flask(__name__)  # create a Flask app
app.config['JSON_SORT_KEYS'] = False 

db_engine = create_engine("sqlite:///data/musical_instrument_reviews.sqlite")
Session = sessionmaker(bind=db_engine)

# Map reviews table to a python object
reviews = Table('reviews', MetaData(bind=db_engine), autoload=True)

@app.route("/", methods=["GET"])
def root() -> Response:
    """
    root - returns 200 OK

    """
    return Response("It's alive! Check", status=200)


@app.route("/v1/products/<product_id>/reviews/stats")
def product_review(product_id: str):
    """
    Shows review statistics for a product.
    Returns a python dictionary with content-type: application/json
    
    """  
    session = Session()

    date = request.args.get('date') # parse a query string formatted as BIGINT unixReviewTime
    
    # SELECT AVG(overall) AS average, COUNT(overall) AS total FROM reviews WHERE productID=<product_id> (AND unixReviewTime=date);
    query_1 = (
        session.query(
            func.avg(reviews.columns.overall)
            .label('average'), 
            func.count(reviews.columns.overall)
            .label('total')
            )
            .filter(reviews.columns.productID==product_id)
        )
    if date:
        query_1 = query_1.filter(reviews.columns.unixReviewTime==date)
    query_1 = query_1.first()
    
    # SELECT overall AS stars, COUNT(overall) AS count FROM reviews WHERE productID=<product_id> (AND unixReviewTime=date) GROUP BY overall;
    query_2 = (
        session.query(
            reviews.columns.overall
            .label('stars'), 
            func.count(reviews.columns.overall)
            .label('count')
            )
            .filter(reviews.columns.productID==product_id)
    )
    if date:
        query_2 = query_2.filter(reviews.columns.unixReviewTime==date)
    query_2 = (
        query_2.group_by(reviews.columns.overall)
        .all()
        )

    try:
        json = {
            "productID": product_id,
            "average": round(query_1.average,1),
            "percent_breakdown": {f"{int(row.stars)}_star": round((row.count*100)/query_1.total) for row in query_2},
            "count_breakdown": {f"{int(row.stars)}_star": row.count for row in query_2},
            "total": query_1.total 
            }
        return json
    except:
        return Response("Error",404) 
    finally:
        session.close()


@app.route("/v1/customers/<customer_id>/reviews/stats")
def customer_review(customer_id: str):
    """
    Shows review statistics for a customer.
    Returns a python dictionary with content-type: application/json
    
    """  
    session = Session()

    date = request.args.get('date') # parse a query string formatted as BIGINT unixReviewTime
    
    # SELECT AVG(overall) AS average, count(overall) AS total FROM reviews WHERE reviewerID=<customer_id> (AND unixReviewTime=date);
    query_1 = (
        session.query(
            func.avg(reviews.columns.overall)
            .label('average'), 
            func.count(reviews.columns.overall)
            .label('total')
            )
            .filter(reviews.columns.reviewerID==customer_id)
        )
    if date:
        query_1 = query_1.filter(reviews.columns.unixReviewTime==date)
    query_1 = query_1.first()

    try:
        json = {
            "customerID": customer_id,
            "average": round(query_1.average,1),
            "total": query_1.total 
            }
        return json
    except:
        return Response("Error",404) 
    finally:
        session.close()
