from .database import db


async def white_list():
    white = db.query("SELECT user_id FROM white_list", fetch='fetchall')
    developer_id_1 = db.query(query="SELECT user_id FROM white_list WHERE super_admin=true", fetch='fetchall')
    developer_id = [item for tup in developer_id_1 for item in tup]
    admins_list_1 = db.query(query="SELECT user_id FROM white_list WHERE admin=true", fetch='fetchall')
    admins_list = [item for tup in admins_list_1 for item in tup]
    step_3 = {}

    for ids in white:
        try:
            try:
                user = db.query(query="SELECT name FROM employee_list WHERE user_id=%s",
                                values=ids, fetch='fetchone')[0]
            except:
                user = db.query("SELECT (user_name, user_surname, username) FROM users WHERE user_id=%s",
                                values=ids,
                                fetch='fetchone')[0]
            if ids[0] in developer_id:
                pass
            elif ids[0] in admins_list:
                try:
                    translator_user = str.maketrans('', '', '()')
                    step_1 = user.translate(translator_user)
                    step_2 = step_1.replace(',', ' ')
                except:
                    step_2 = user
                step_3[f'white_{ids[0]}'] = '[ADM] ' + step_2
            else:
                try:
                    translator_user = str.maketrans('', '', '()')
                    step_1 = user.translate(translator_user)
                    step_2 = step_1.replace(',', ' ')
                except:
                    step_2 = user
                step_3[f'white_{ids[0]}'] = step_2
        except:
            pass
    return step_3


async def admins_lists():
    developer_id_1 = db.query(query="SELECT user_id FROM white_list WHERE super_admin=true", fetch='fetchall')
    developer_id = [item for tup in developer_id_1 for item in tup]
    admins_list_1 = db.query(query="SELECT user_id FROM white_list WHERE admin=true", fetch='fetchall')
    admins_list = [item for tup in admins_list_1 for item in tup]
    admins_list.extend(developer_id)
    admins_list = [int(d) for d in admins_list]
    return admins_list


async def check_stop_list():
    data = db.query(query="SELECT * FROM stop_list ORDER BY name", fetch='fetchall')
    result = {}

    for org_id, name, item_id, date_add in data:
        org_name = db.query('SELECT name FROM organizations WHERE org_id=%s', values=(org_id,), fetch='fetchone')[0]
        if org_name not in result:
            result[org_name] = {
                "items": []
            }
        result[org_name]["items"].append({
            "name": name,
            "item_id": item_id,
            "date_add": date_add
        })
    return result


async def stop_list_differences(dict_a, dict_b):
    result = {}
    for key, value in dict_a.items():
        result[key] = {'items': []}
        for item in value['items']:
            if key not in dict_b or not any(
                    existing_item['item_id'] == item['item_id'] for existing_item in dict_b[key]['items']):
                result[key]['items'].append(item)
    return result



