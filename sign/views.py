from django.shortcuts import render
#from django.http import HttpResponse
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from sign.models import Event,Guest
from django.core.paginator import Paginator,EmptyPage,PageNotAnInteger
from django.shortcuts import render, get_object_or_404


# Create your views here.
def index(request):
    return render(request,"index.html")
#    return HttpResponse("Hello Django --- Qingbo!")

def login_action(request):
    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        user = auth.authenticate(username=username, password=password)
        #if username == 'admin' and password == 'admin123':
        if user is not None:
            auth.login(request,user) #登录
            #return HttpResponseRedirect('/event_manage/')

            #response.set_cookie('user', username, 5) # 添加浏览器cookie
            request.session['user']=username  # 将 session 信息记录到浏览器
            response = HttpResponseRedirect('/event_manage/')
            return response
        else:
            return render(request,'index.html', {'error': 'username or password error!'})

@login_required
def event_manage(request):
    #return render(request,"event_manage.html")
    #username = request.COOKIES.get('user', '') # 读取浏览器cookie
    event_list=Event.objects.all()
    username=request.session.get('user','') # 读取浏览器 session
    return render(request,"event_manage.html",{"user":username,"events":event_list})

@login_required
def search_name(request):
    username=request.session.get('user','')
    search_name=request.GET.get("name","")
    event_list=Event.objects.filter(name__contains=search_name)
    return render(request,"event_manage.html",{"user":username,"events":event_list})

# 嘉宾管理
@login_required
def guest_manage(request):
    username = request.session.get('user', '')
    guest_list = Guest.objects.all()
    paginator=Paginator(guest_list,2)
    page=request.GET.get('page')
    try:
        contacts=paginator.page(page)
    except PageNotAnInteger:
        contacts=paginator.page(1)
    except EmptyPage:
        contacts=paginator.page(paginator.num_pages)
    return render(request, "guest_manage.html", {"user": username, "guests": contacts})
    #return render(request, "guest_manage.html", {"user": username, "guests": guest_list})
# # 签到页面
# @login_required
# def sign_index(request,eid):
#     event=get_object_or_404(Event,id=eid)
#     return render(request,'sign_index.html',{'event':event})

# 签到动作
@login_required
def sign_index_action(request,eid):
    event = get_object_or_404(Event, id=eid)
    phone = request.POST.get('phone','')
    print(phone)
    result = Guest.objects.filter(phone = phone)
    if not result:
        return render(request, 'sign_index.html', {'event': event, 'hint': 'Phone Error.'})
    result = Guest.objects.filter(phone=phone,event_id=eid)
    if not result:
        return render(request, 'sign_index.html', {'event': event, 'hint':'Event ID or Phone Error.'})
    result = Guest.objects.get(phone=phone,event_id=eid)
    if result.sign:
        return render(request, 'sign_index.html', {'event': event, 'hint': "User Has Sign In."})
    else:
        Guest.objects.filter(phone=phone,event_id=eid).update(sign = '1')
        return render(request, 'sign_index.html', {'event': event, 'hint':'Sign In Success!', 'guest': result})

# 退出登录
@login_required
def logout(request):
    auth.logout(request) #退出登录
    response = HttpResponseRedirect('/index/')
    return response
