from django.shortcuts import render, redirect
from django.http import HttpResponse
# Create your views here.
from .models import Doctor, DoctorQuery
from coins.models  import CoinWallet

def doctor_list(request):
    doctors = Doctor.objects.all()
    return render(request, 'doctors/doctor_list.html', {'doctors': doctors})

def ask_doctor(request, doctor_id):
    if request.method == 'POST':
        doctor = Doctor.objects.get(id=doctor_id)
        query = request.POST.get('query')
        wallet = CoinWallet.objects.get(user=request.user)
        if wallet.balance >=50:
            wallet.withdraw(50)
            DoctorQuery.objects.create(user= request.user, doctor=doctor, query=query)
        else:
            return HttpResponse('Insufficient funds')
        return redirect('home')
