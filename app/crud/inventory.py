from sqlalchemy.orm import Session
from app.models.inventory import Inventory

def create_inventory(db:Session,p_id:int,total_stock : int ,available_stock:int , locked_stock:int):
    iven=Inventory(p_id,total_stock,available_stock,locked_stock)
    db.add(iven)
    db.commit()
    db.refresh(iven)
    return iven

def update_inventory(db:Session,id:int,**kwargs):
    inventory=db.query(Inventory).filter(Inventory.id==id).first()
    if not inventory:
        return None
    for key , value in kwargs.items():
        if hasattr(inventory,key):
            setattr(inventory,key,value)
    db.commit()
    db.refresh(inventory)
    return inventory



def delete_inventory(db:Session,id:int):
    inventory=db.query(Inventory).filter(Inventory.id==id).first()
    if inventory:
        db.delete(inventory)
        db.commit()
        return True
    return False


def get_inventory_by_id(db:Session,id:int):
    inventory=db.query(Inventory).filter(Inventory.id==u_id).first()
    return inventory

def get_inventory_by_pid(db:Session,p_id:int):
    inventory=db.query(Inventory).filter(Inventory.p_id==p_id).first()
    return inventory
