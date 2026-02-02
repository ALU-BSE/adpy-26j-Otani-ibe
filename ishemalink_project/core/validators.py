def validate_rwanda_nid(nid_number):
    nid_str = str(nid_number)
    
    if len(nid_str) == 16:
        if nid_str.isdigit() == True:
            if nid_str.startswith("1") == True:
                return True
            else:
                print("Error: must start with 1")
                return False
        else:
            print("Error: not all numbers")
            return False
    else:
        print("Error: length is not 16, it is " + str(len(nid_str)))
        return False