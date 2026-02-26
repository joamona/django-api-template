import sys

from buildings.insert import insert as insert_building
from buildings.select import select as select_building
from buildings.update import update as update_building
from buildings.delete import delete as delete_building

def main():
    # sys.argv[0] es siempre el nombre del archivo (main.py)
    # Por eso verificamos que haya al menos 3 elementos (nombre + p1 + p2)
    if len(sys.argv) == 3:
        tableName = sys.argv[1]
        functionName = sys.argv[2]        
    else:
        print("Error: You mus give two parameters tableName and functionName to execute the addecuate function.")
        sys.exit(0)


    if tableName not in ["buildings", "trees", "water"]:
        print("Error: The available table names are buildings, trees, water")
        sys.exit(0)
    
    if functionName not in ["insert", "select", "update", "delete"]:
        print("Error the available function names are insert, select, delete or update")
        sys.exit(0)

    if tableName == "buildings":
        if functionName=="insert":
            insert_building()
        elif functionName=="select":
            select_building()
        elif functionName=="update":
            update_building()
        elif functionName=="delete":
            delete_building()
    elif tableName=="trees":
        if functionName=="insert":
            pass
        elif functionName=="select":
            pass
        elif functionName=="update":
            pass
        elif functionName=="delete":
            pass

if __name__ == "__main__":
    main()

