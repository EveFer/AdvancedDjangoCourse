import csv

def import_csv(filename): 
    with open(filename) as csvarchivo:
        entrada=csv.DictReader(csvarchivo)
        for reg in entrada:
            if int(reg['members_limit'])!=0:
                Circle.objects.create( 
                name=reg['name'], 
                slug_name=reg['slug_name'], 
                is_public=reg['is_public'], 
                verifed=reg['verifed'], 
                is_limited=1, 
                members_limit=reg['members_limit']) 
                print(reg['name']) 
            else:
                Circle.objects.create( 
                name=reg['name'], 
                slug_name=reg['slug_name'], 
                is_public=reg['is_public'], 
                verifed=reg['verifed'],  
                members_limit=reg['members_limit']) 
                print(reg['name'])
