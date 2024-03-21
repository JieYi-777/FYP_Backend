from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from .models import User, Budget
from . import db
import logging

# Create Blueprint object
budget = Blueprint('budget', __name__)

# Get a logger for logging
logger = logging.getLogger(__name__)
