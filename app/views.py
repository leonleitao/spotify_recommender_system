from flask import Blueprint
from flask import Flask, render_template, url_for, redirect, request, session, jsonify, flash, Blueprint

view = Blueprint("views", __name__,template_folder='templates',static_folder='static')

@view.route("/")
@view.route("/home")
def home():
    return render_template('home.html')

@view.route("/recommendations")
def recommendations():
    return render_template('recommendations.html')