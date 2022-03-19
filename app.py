#type:ignore
from flask import Flask,request,jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

app=Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"]="sqlite:///todos.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False

db=SQLAlchemy(app)
ma=Marshmallow(app)

class Todo(db.Model):
    __tablename__="todos"
    id=db.Column(db.Integer, primary_key=True)
    todo=db.Column(db.String(50), nullable=False)
    description=db.Column(db.String(500))
    complete=db.Column(db.Boolean, default=False)

    def __init__(self,todo,description):
        self.todo=todo
        self.description=description

class TodoSchema(ma.Schema):
    class Meta:
        fields=('id','todo','description','complete')

todo_serializer=TodoSchema()
todos_serializer=TodoSchema(many=True)

@app.get("/")
def allTodos():
    todos=Todo.query.all()
    todos=todos_serializer.dump(todos)

    return todos_serializer.jsonify(todos),200

@app.get("/<todoId>")
def getTodoById(todoId):
    todo=Todo.query.filter_by(id=todoId).first()

    if todo == None: #if todo doesnt exist return message
        return {"msg":"no such todo"},404

    todo=todo_serializer.dump(todo)

    return jsonify(todo),200

@app.post("/")
def addTodo():
    try:
        data=request.json
        todo=Todo(data['todo'],data['description'])
        db.session.add(todo)
        db.session.commit()

        return {"msg":"todo created successfuly"},201

    except:
        return {"msg":"failed to create a todo"},406

@app.put("/<todoId>")
def updateTodo(todoId):
    try:
        data=request.json
        todo=Todo.query.filter_by(id=todoId).first()
        todo.todo=data['todo']
        todo.description=data['description']
        db.session.commit()

        todo=todo_serializer.dump(todo)

        return jsonify({ "todo":todo, "msg":"todo updated successfuly"}),201

    except:
        return {"msg":"failed to  updated todo"} ,406

@app.patch("/<todoId>")
def completeTodo(todoId):
    todo=Todo.query.filter_by(id=todoId).first()

    if todo == None: #if todo doesnt exist return message
        return {"msg":"no such todo"},404

    todo.complete=True
    db.session.commit()
    todo=todo_serializer.dump(todo)
    return jsonify({"todo":todo,"msg":"completed todo successfully"}),200

@app.delete("/<todoId>")
def deleteTodo(todoId):
    todo=Todo.query.filter_by(id=todoId).first()

    if todo == None: #if todo doesnt exist return message
        return {"msg":"no such todo"},404

    db.session.delete(todo)
    db.session.commit()

    return {"msg":"deleted todo successfuly"},200


if __name__=="__main__":
    db.create_all()
    app.run(debug=True)