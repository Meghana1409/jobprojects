import requests
import urllib.parse
from bs4 import BeautifulSoup
import re
import datetime
from .models import FarDetailsAll
from ipaddress import ip_address

x = datetime.datetime.now()

todat_date=x.strftime("%Y-%m-%d")

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Content-Type": "application/x-www-form-urlencoded"
}
payload = {
    "user": "eisadmin",
    "pass": "Password1@5"
}

session=requests.Session()
session.headers.update(headers)


def data_serializer_farDB(farData):
    far_Id=set()
    subject=set()
    status=set()
    zone=set()
    Requested_Source=set()
    Requested_Destination=set()
    Change_Service=set()
    if len(farData)==1:
       print("only one value found")
       for far in farData:
           return {"Subject":far["Subject"],"Status":far["Status"],"ZONE":far["ZONE"],"Requested_Source":far["Requested_Source"],"Requested_Destination":far["Requested_Destination"],"Change_Service":far["Change_Service"]}
    for far in  farData:
        far_Id.add(far["Far_Id"])
        subject.add(far["Subject"])
        status.add(far["Status"])
        zone.add(far["ZONE"])
        Requested_Source.add(far["Requested_Source"])
        Requested_Destination.add(far["Requested_Destination"])
        Change_Service.add(far["Change_Service"])
    subject=list(subject)
    status=list(status)
    zone=list(zone)
    Requested_Source=list(Requested_Source)
    Requested_Destination=list(Requested_Destination)
    Change_Service=list(Change_Service)
    if(len(subject) == 1 ):
        subject=str(subject[0])
    if(len(status) == 1 ):
        status=str(status[0])
    if(len(subject) == 1 ):
        zone=str(zone[0])
    if(len(Requested_Source) == 1 ):
        Requested_Source=str(Requested_Source[0])
    if(len(Requested_Destination) == 1 ):
        Requested_Destination=str(Requested_Destination[0])
    if(len(Change_Service) == 1 ):
        Change_Service=str(Change_Service[0])
    return {"Subject":subject,
            "Status":status,
            "ZONE":zone,
            "Requested_Source":Requested_Source,"Requested_Destination":Requested_Destination,"Change_Service":Change_Service}





def get_far_db(request,user_dict):
    filters={}
    filtercreate=""
    filterexpire=""
    key_ip=''
    target_ip=''
    #return {"Subject":"thiswas","Requested Source":"this was the source"}
    for key,val in user_dict.items():
        if val :
            if key == "filterexpired" :
                filterexpire=val
            elif key == "filtercreated":
                filtercreate=val
            elif key == "Created":
                if filtercreate == "Before":
                    filters[f"{key}__lte"]=val
                else:
                    filters[f"{key}__gte"]=val
            elif key == "Expires":
                if filterexpire == "Before":
                    filters[f"{key}__lte"]=val
                else:
                    filters[f"{key}__gte"]=val
            elif key == "Requested_Source" or key == "Requested_Destination":
                #key_ip,target_ip = key,ip_address(val)
                key_ip,target_ip = key,val
                #filters[f"{key}__icontains"]=val
            else:
                filters[f"{key}__icontains"]=val
    #print(filters)
    Fardata=None
    farlen=1
    FarNew=None
    Fardata = FarDetailsAll.objects.filter(**filters).values()
    if(len(Fardata)>1):
       FarNew=data_serializer_farDB(Fardata)
    if key_ip:
        #print("key_ip:",ip_address(val))
        for obj in Fardata:
            ipaddr= obj[key_ip].strip().split(',')
            print(ipaddr)
            if(ipaddr[0] == 'any' and ipaddr == target_ip):
                Fardata=[obj]
                break
            else:
                for i in ipaddr:
                    ips = i.split('-')
                    start=ips[0].strip().split('/')[0]
                    if len(ips) > 1:
                        end=ips[1].strip()
                        #print("ip_address(start)",type(ip_address(start)),"target_ip",type(target_ip),"ip_address(end)",type(ip_address(end)))
                        if ip_address(start) <= ip_address(target_ip) <= ip_address(end):
                            Fardata=[obj]
                            break
                        else:
                            if ip_address(start) == ip_address(target_ip):
                                Fardata=[obj]
                                break
                #except:
                #    print("False")
    #print(f'this is the length of data fetched from the db{len(FarNew["Subject"])}')
    print(f'this is the length fro far db of data fetched from the db{Fardata}')

    lent=len(Fardata)
    print(lent)
    if(lent > 0):
        if(lent == 1):
            print("in the awailting details section ")
            far=Fardata[0]
            request.session["details"]=far
            request.session["conversation_state"] = "awaiting_details"
            print(f"this is the value for far {far['Subject']}")
            #try:
            return (f"FAR ID : <b>{far['Far_Id']}</b> is raised for <b>{far['Subject']} </b> which is now at <b>{far['Status']}</b> ","do you want more details?:\n1.YES\n2.No\ny.Back\nz.Main Menu")
            #except Exception as e:
            #    print("was not able to convert the details")
        else:
            print("###############################in awaiting_details")
            Fardata=FarNew
            #FAR_list='\n'.join([f"{chr(i)}. {far['Far_Id']} : {far['Subject']}" for i, far in enumerate(Fardata,97)])
            #request.session["conversation_state"] = "awaiting_id"
            #return ("Multiple matches found",f"\nPlease select one by name.:\n{FAR_list}\ny.back\nz.main menu")
            #return ("Multiple matches found",f"\nPlease select one by name.:\n\ny.back\nz.main menu")
            return Fardata
    else:
        request.session["details"]=user_dict
        request.session["conversation_state"] = "awaiting_id"
        return ("My Database don't have data related to this Far.""Do you want me to search data in portal and give data to you?","\n1.YES\n2.NO\ny.back\nz.Main Menu")

def get_far_info(request,user_dict):
    print(user_dict)
    if 'Far_Id' in user_dict:
        far_id=str(user_dict['Far_Id'])
        url = "https://nspm.sbi/FireFlow/Ticket/Display.html?id="+far_id
    #response = requests.post(url, data=payload, headers=headers, verify=False)
        response=session.post(url,data=payload,headers=headers,verify=False)
        decoded=urllib.parse.unquote(response.text)
        soup = BeautifulSoup(decoded, 'html.parser')
        try:
            titles=soup.find_all('table', {'class': 'ticket-summary'})
            summary=[tag for tag in titles[0].find_all(class_="titlebox-content") if tag.name != "script"]
            print(summary)
            basic_dict={'Far_Id':far_id}
            basic_title=summary[0].find_all(class_="labeltop")
            basic_values=summary[0].find_all(class_="value")
            for i in range(len(basic_title)):
                basic_dict[basic_title[i].get_text().strip()]=basic_values[i].get_text()
            print("basic_dict 0:",basic_dict)
            general_title=summary[2].find_all(class_="labeltop")
            general_values=summary[2].find_all(class_="value")
            for i in range(len(general_title)):
                basic_dict[general_title[i].get_text().strip()]=general_values[i].get_text()
            print("basic_dict 2:",basic_dict)
            add_info=summary[3].find_all(class_="labeltop")
            add_info_values=summary[3].find_all(class_="value")
            for i in range(len(add_info)):
                basic_dict[add_info[i].get_text().strip()]=add_info_values[i].get_text()
            print("basic_dict 3:",basic_dict)
            print("summary4: ",summary[4])
            #print("summary5: ",summary[5])
            original_req=summary[4].find_all(class_="label")
            original_value=summary[4].find_all(class_="value")
            for i in range(len(original_req)):
                basic_dict[original_req[i].get_text().strip()]=[original_value[i].get_text(),original_value[i+len(original_req)+2].get_text()]
            print("basic_dict 4:",basic_dict)
            request.session["details"]=basic_dict
            request.session["conversation_state"] = "awaiting_details"
            return (f"FAR ID {user_dict['Far_Id']} is raised for <b>{basic_dict['Subject:']} </b> which is now at <b>{basic_dict['Status:']}</b> ","do you want more details?:\n1.YES\n2.No")
        except:
            basic_dict="Far Not Found"
            #request.session["conversation_state"] = "awaiting_selection":
        print(basic_dict)
        return basic_dict
    else:
        return get_advanced_far_search(request,user_dict)


#def get_advanced_far_search(farid="",subject="",department="",source="",destination="",port=""):
def get_advanced_far_search(request,user_dict):
    url = "https://nspm.sbi/FireFlow/Search/Build.html"
    header_adv=headers

    payload = {
    "user": "eisadmin",
    "pass": "Password1@4"
    }

    header_adv["Referer"]="https://nspm.sbi/FireFlow/Search/Build.html"
    header_adv["Origin"]="https://nspm.sbi/"
    session.headers.update(header_adv)
    resp=session.post(url,data=payload,verify=False)
    fin_resp=session.get(url,verify=False)
    soup=BeautifulSoup(fin_resp.text, 'html.parser')
    form = soup.find_all('form')[1]
    post_url=form.get('action')
    if not post_url.startswith("http"):
        post_url=requests.compat.urljoin(url,post_url)

    payloads={}
    for input_tag in form.find_all('input'):
        name=input_tag.get('name')
        value=input_tag.get('value','')
        if name:
            payloads[name]= value
    if "Subject"  in user_dict:
        payloads["AttachmentField"]= "Subject"
        payloads["AttachmentOp"]= "LIKE"
        payloads["ValueOfAttachment"]=user_dict["Subject"]
    if "Requested_Source"  in user_dict:
        payloads["'CF.{Requested Source}'Op"]= "LIKE"
        payloads["ValueOf'CF.{Requested Source}'"] = user_dict["Requested_Source"]
    if "Requested_Destination"  in user_dict:
        payloads["'CF.{Requested Destination}'Op"]= "LIKE"
        payloads["ValueOf'CF.{Requested Destination}'"]=user_dict["Requested_Destination"]
    if "Requested_Service" in user_dict:
        payloads["'CF.{Requested Service}'Op"]= "LIKE"
        payloads["ValueOf'CF.{Requested Service}'"]= 'tcp/'+user_dict["Requested_Service"]
    if "ZONE" in user_dict:
        payloads["'CF.{ZONE}'Op"]= "LIKE"
        payloads["ValueOf'CF.{ZONE}'"]=user_dict["ZONE"]
    payloads["AndOr"]= "AND"
    payloads["OrderBy"]="id"
    payloads["Order"]="ASC"

    final_resp=session.post(url,data=payloads,verify=False)
    final_soup=BeautifulSoup(final_resp.text, 'html.parser')
    try:
        ticket_list={}
        tickets=final_soup.find('table',{'class':'ticket-list'}).find_all('tr')
        for i in tickets:
            tds=i.find_all('td')
            if(len(tds)>1):
                ticket_id=tds[0].text
                ticket_subject=tds[1].text
                if ticket_subject not in ticket_list:
                    ticket_list[ticket_subject]=ticket_id
    except:
        ticket_list="Portal don't have data related to this Far."
        request.session["conversation_state"] = "awaiting_selection"


    return ticket_list
