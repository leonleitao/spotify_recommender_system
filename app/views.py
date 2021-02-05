from flask import Blueprint
from flask import Flask, render_template, url_for, redirect, request, session, jsonify, flash, Blueprint

view = Blueprint("views", __name__)

@view.route("/")
@view.route("/home")
def home():
    return "<h1>Home Page</h1>"

@view.route("/recommendations")
def recommendations():
    return "<h1>Recommendations Page</h1>"