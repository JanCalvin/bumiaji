from django.shortcuts import render, redirect
from . import models
from datetime import datetime
import calendar
# from .decorators import role_required
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth import login , logout, authenticate
from django.contrib.auth.decorators import login_required
from django.forms import inlineformset_factory
from django.forms import DateInput
from django.db import transaction
from django.core.exceptions import ValidationError
import json
# from weasyprint import HTML
from django.template.loader import render_to_string
import tempfile
# Create your views here.
from django.db.models import Q,Sum,Value
import math

konversi_produk_to_komoditas = {'Pastry':('Jambu Kristal',0.33),
            'Teh Bunga Telang' :('Bunga Telang',0.1),
            'Lemon Kering' :('Lemon',0.2),
            'Keripik Cale' :('Cale',0.25),
            'Rujak Jambu Kristal' : ('Jambu Kristal', 0.4)
            }
bulan_indo = {
    'January': 'Januari',
    'February': 'Februari',
    'March': 'Maret',
    'April': 'April',
    'May': 'Mei',
    'June': 'Juni',
    'July': 'Juli',
    'August': 'Agustus',
    'September': 'September',
    'October': 'Oktober',
    'November': 'November',
    'December': 'Desember'
    }
# CRUD MITRA
def read_mitra(request) :
    allmitra = models.mitra.objects.all()
    if not allmitra.exists():
        messages.error(request, "Data Mitra Tidak Ditemukan!")
    return render(request,
                  'mitra/read_mitra.html',
                  {
                      'allmitra': allmitra
                  })

def create_mitra(request) :
    
    if request.method == "GET" :
        return render(request, 
                      'mitra/create_mitra.html')
    else :
        namamitra = request.POST["nama_mitra"]
        mitraobj = models.mitra.objects.filter(nama_mitra=namamitra)
        
        if len(mitraobj) >0:
            messages.error(request,"Nama Mitra Sudah Ada")
        else :
            alamatmitra = request.POST["alamat_mitra"]
            nohpmitra = request.POST["nohp_mitra"]
            tanggalawalmitra = request.POST["tanggalawal_mitra"]
            durasikontrakmitra = request.POST["durasi_kontrak"]
            luaslahan = request.POST["luas_lahan"]
            status = request.POST["status_mitra"]
            if status.lower() == "aktif" :
                statusmitra = True
            else :
                statusmitra = False
            models.mitra(
                nama_mitra = namamitra,
                alamat_mitra = alamatmitra,
                nohp_mitra = nohpmitra,
                tanggalawal_mitra = tanggalawalmitra,
                durasi_kontrak = durasikontrakmitra,
                luas_lahan = luaslahan,
                status_mitra = statusmitra
            ).save()

            messages.success(request,"Data Mitra Berhasil Ditambahkan!")
        return redirect("read_mitra")
            

    
def update_mitra(request, id):
    try:
        getmitraobj = models.mitra.objects.get(id_mitra=id)
    except models.mitra.DoesNotExist:
        messages.error(request, "Mitra tidak ditemukan!")
        return redirect('read_mitra')

    if request.method == "GET":
        tanggal = getmitraobj.tanggalawal_mitra.strftime('%Y-%m-%d')  # Format tanggal
        statusmitra = 'Aktif' if getmitraobj.status_mitra else 'Tidak Aktif'
        return render(request, 'mitra/update_mitra.html', {
            'getmitraobj': getmitraobj,
            'statusmitra': statusmitra,
            'tanggal': tanggal
        })
    else:
        namamitra = request.POST["nama_mitra"]
        if models.mitra.objects.filter(nama_mitra=namamitra).exclude(id_mitra=id).exists():
            messages.error(request, "Nama Mitra Sudah Ada!")
            return redirect('read_mitra')

        # Perbarui objek mitra
        getmitraobj.nama_mitra = namamitra
        getmitraobj.alamat_mitra = request.POST["alamat_mitra"]
        getmitraobj.nohp_mitra = request.POST["nohp_mitra"]
        getmitraobj.tanggalawal_mitra = request.POST["tanggalawal_mitra"]
        getmitraobj.durasi_kontrak = request.POST["durasi_kontrak"]
        getmitraobj.luas_lahan = request.POST["luas_lahan"]
        getmitraobj.status_mitra = request.POST["status_mitra"].lower() == "aktif"
        
        getmitraobj.save()
        messages.success(request, "Mitra berhasil diperbarui!")
        return redirect('read_mitra')
            
    
def delete_mitra(request,id) :
    getmitraobj = models.mitra.objects.get(id_mitra = id)
    getmitraobj.delete()
    messages.success(request, "Data berhasil dihapus!")
    return redirect('read_mitra')

'''CRUD PENJUALAN'''
def read_penjualan(request) : 
    penjualanobj = models.penjualan.objects.all()
    if not penjualanobj.exists():
        messages.error(request, "Data Penjualan Tidak Ditemukan!")
    return render(request,
                  'penjualan/read_penjualan.html',
                  {
                      'penjualanobj': penjualanobj
                  })

def create_penjualan(request) :
    #Data yang harus diambil sebelum masuk ke 'get'/'post'
    # detailpanenlobj = 
    pasarobj = models.pasar.objects.all()
    produkobj = models.produk.objects.all()
    komoditasobj = models.komoditas.objects.all()
    if request.method == 'GET' :
        return render(request, 'penjualan/create_penjualan.html',{
            'pasarobj' : pasarobj,
            'produkobj' : produkobj,
            'komoditasobj' : komoditasobj,
        })
    
    else :
        #Mengambil data yang ingin di 'post' dari input html
        pasar = request.POST['pasar']
        tanggal = request.POST['tanggal']
        kuantitasp = request.POST.getlist('kuantitasp')
        kuantitask = request.POST.getlist('kuantitask')
        produk = request.POST.getlist('produk')
        komoditas = request.POST.getlist('komoditas')

        print(kuantitasp)
        print(kuantitask)
        print(produk)
        print(komoditas)
        #request.POST.getlist
        #for a,b,c,d in zip(a,b,c,d)


        penjualan = models.penjualan(
            id_pasar = models.pasar.objects.get(id_pasar = pasar),
            tanggal = tanggal,
        )
        penjualan.save()

        id = penjualan.id_penjualan

        for produk,komoditas,kuantitasp,kuantitask in zip(produk,komoditas,kuantitasp,kuantitask) :
            if komoditas != '' and produk != '' and kuantitasp != '' and kuantitask != '' :
                detail = models.detailpenjualan(
                    id_penjualan = models.penjualan.objects.get(id_penjualan = id),
                    id_produk = models.produk.objects.get(id_produk = produk),
                    id_komoditas = models.komoditas.objects.get(id_komoditas = komoditas),
                    kuantitas_produk = kuantitasp,
                    kuantitas_komoditas = kuantitask,
                )

            elif komoditas != '' and produk == '' and kuantitasp == '' and kuantitask != '' :
                detail = models.detailpenjualan(
                    id_penjualan = models.penjualan.objects.get(id_penjualan = id),
                    id_produk = None,
                    id_komoditas = models.komoditas.objects.get(id_komoditas = komoditas),
                    kuantitas_produk = None,
                    kuantitas_komoditas = kuantitask,
                )
            
            elif komoditas == '' and produk != '' and kuantitasp != '' and kuantitask == '' :
                detail = models.detailpenjualan(
                    id_penjualan = models.penjualan.objects.get(id_penjualan = id),
                    id_produk = models.produk.objects.get(id_produk = produk),
                    id_komoditas = None,
                    kuantitas_produk = kuantitasp,
                    kuantitas_komoditas = None,
                )

            else :
                getpenjualan = models.penjualan.objects.get(id_penjualan = id)
                getdetailpenjualan = models
                getpenjualan.delete()
                messages.error(request, 'Data Penjualan minimal memiliki produk/komoditas dan kuantitas yang sesuai, Coba Ulang Kembali!')
                return redirect('create_penjualan')
        detail.save()
        messages.success(request, 'Data Penjualan Berhasil Ditambahkan!')
        return redirect('read_penjualan')
    
def update_penjualan(request, id) :
    pass

def delete_penjualan(request, id) :
    getpenjualan = models.penjualan.objects.get(id_penjualan = id)
    getpenjualan.delete()
    messages.success(request, "Data Penjualan berhasil dihapus!")
    return redirect('read_penjualan')


'''PANEN MITRA'''

def read_panenmitra(request) :
    panenmitra = models.detailpanenmitra.objects.all()
    if not panenmitra.exists() :
        messages.error(request, 'Data Panen Mitra Tidak Ditemukan!')
        return render(request,'panen/panenmitra/read_panenmitra.html')
    else :

        

        return render(request,'panen/panenmitra/read_panenmitra.html',{
            'panenmitra' : panenmitra,
        })

def create_panenmitra(request) :
    filtermitra = models.mitra.objects.filter(status_mitra = True)
    allkomoditas = models.komoditas.objects.all()
    if request.method == "GET" :
        return render(request, 
                      'panen/panenmitra/create_panenmitra.html',{
                            'filtermitra' : filtermitra,
                            'allkomoditas' : allkomoditas,
                      })
    else :
        nama_mitra = request.POST["nama_mitra"]
        tanggal_panen = request.POST["tanggal_panen"]
        komoditas = request.POST.getlist("komoditas")
        batch = request.POST.getlist("batch")
        kadaluwarsa = request.POST.getlist("kadaluwarsa")
        kuantitas = request.POST.getlist("kuantitas")
       
        panen_mitra = models.panenmitra(
            id_mitra = models.mitra.objects.get(id_mitra=nama_mitra),
            tanggal_panen = tanggal_panen
        )

        panen_mitra.save()
       
        for komoditas,batch,kadaluwarsa,kuantitas in zip(komoditas,batch,kadaluwarsa,kuantitas) :
            models.detailpanenmitra(
                idpanen_mitra = panen_mitra,
                id_komoditas = models.komoditas.objects.get(
                    id_komoditas = komoditas
                ),
                batch = batch,
                tanggal_kadaluwarsa = kadaluwarsa,
                kuantitas = kuantitas,
            ).save()

        messages.success(request,"Data Panen Mitra Berhasil Ditambahkan!")
        return redirect("read_panenmitra")
            

    
def update_panenmitra(request, id):
    try:
        getdetailobj = models.detailpanenmitra.objects.get(iddetailpanen_mitra=id)
        
    except models.detailpanenmitra.DoesNotExist:
        messages.error(request, "Data Panen Mitra tidak ditemukan!")
        return redirect('read_panenmitra')
    filtermitra = models.mitra.objects.filter(status_mitra = True)
    allkomoditas = models.komoditas.objects.all()
  
    if request.method == "GET":
        tanggal_panen = getdetailobj.idpanen_mitra.tanggal_panen.strftime('%Y-%m-%d')  # Format tanggal
        tanggal_kadaluwarsa = getdetailobj.tanggal_kadaluwarsa.strftime('%Y-%m-%d')  # Format tanggal
        return render(request, 'panen/panenmitra/update_panenmitra.html', {
            'getdetailobj': getdetailobj,
            'filtermitra' : filtermitra,
            'allkomoditas' : allkomoditas,
            'tanggal_panen': tanggal_panen,
            'tanggal_kadaluwarsa': tanggal_kadaluwarsa
        })
    else:     
        # Perbarui objek mitra
        getmitra = models.mitra.objects.get(id_mitra=request.POST["nama_mitra"])
        getkomoditas =models.komoditas.objects.get(id_komoditas=request.POST["komoditas"])

        getdetailobj.idpanen_mitra.id_mitra = getmitra
        getdetailobj.idpanen_mitra.tanggal_panen = request.POST["tanggal_panen"]
        getdetailobj.id_komoditas = getkomoditas
        getdetailobj.batch = request.POST["batch"]
        getdetailobj.tanggal_kadaluwarsa = request.POST["kadaluwarsa"]
        getdetailobj.kuantitas = request.POST["kuantitas"]

        getdetailobj.idpanen_mitra.save()
        getdetailobj.save()
        
        messages.success(request, "Data panen mitra berhasil diperbarui!")
        return redirect('read_panenmitra')
            
    
def delete_panenmitra(request,id) :
    getdetailobj = models.detailpanenmitra.objects.get(iddetailpanen_mitra = id)
    getdetailobj.delete()
    messages.success(request, "Data berhasil dihapus!")
    return redirect('read_panenmitra')

'''PANEN LOKAL'''

def read_panenlokal(request) :
    panenlokal = models.detailpanenlokal.objects.all()
    if not panenlokal.exists() :
        messages.error(request, 'Data Panen lokal Tidak Ditemukan!')
        return render(request,'panen/panenlokal/read_panenlokal.html')
    else :

        return render(request,'panen/panenlokal/read_panenlokal.html',{
            'panenlokal' : panenlokal,
        })

def create_panenlokal(request) :
    
    allkomoditas = models.komoditas.objects.all()
    if request.method == "GET" :
        return render(request, 
                      'panen/panenlokal/create_panenlokal.html',{
                            'allkomoditas' : allkomoditas,
                      })
    else :
        tanggal_panen = request.POST["tanggal_panen"]
        komoditas = request.POST.getlist("komoditas")
        batch = request.POST.getlist("batch")
        kadaluwarsa = request.POST.getlist("kadaluwarsa")
        kuantitas = request.POST.getlist("kuantitas")
       
        panen_lokal = models.panenlokal(
            tanggal_panen = tanggal_panen
        )

        panen_lokal.save()

        for komoditas,batch,kadaluwarsa,kuantitas in zip(komoditas,batch,kadaluwarsa,kuantitas) :
            models.detailpanenlokal(
                idpanen_lokal = panen_lokal,
                id_komoditas = models.komoditas.objects.get(
                    id_komoditas = komoditas
                ),
                batch = batch,
                tanggal_kadaluwarsa = kadaluwarsa,
                kuantitas = kuantitas,
            ).save()

        messages.success(request,"Data Panen lokal Berhasil Ditambahkan!")
        return redirect("read_panenlokal")
            

    
def update_panenlokal(request, id):
    try:
        getdetailobj = models.detailpanenlokal.objects.get(iddetailpanen_lokal=id)
        
    except models.detailpanenlokal.DoesNotExist:
        messages.error(request, "Data Panen lokal tidak ditemukan!")
        return redirect('read_panenlokal')
    allkomoditas = models.komoditas.objects.all()
  
    if request.method == "GET":
        tanggal_panen = getdetailobj.idpanen_lokal.tanggal_panen.strftime('%Y-%m-%d')  # Format tanggal
        tanggal_kadaluwarsa = getdetailobj.tanggal_kadaluwarsa.strftime('%Y-%m-%d')  # Format tanggal
        return render(request, 'panen/panenlokal/update_panenlokal.html', {
            'getdetailobj': getdetailobj,
            'allkomoditas' : allkomoditas,
            'tanggal_panen': tanggal_panen,
            'tanggal_kadaluwarsa': tanggal_kadaluwarsa
        })
    else:     
    
        getkomoditas =models.komoditas.objects.get(id_komoditas=request.POST["komoditas"])

        getdetailobj.idpanen_lokal.tanggal_panen = request.POST["tanggal_panen"]
        getdetailobj.id_komoditas = getkomoditas
        getdetailobj.batch = request.POST["batch"]
        getdetailobj.tanggal_kadaluwarsa = request.POST["kadaluwarsa"]
        getdetailobj.kuantitas = request.POST["kuantitas"]

        getdetailobj.idpanen_lokal.save()
        getdetailobj.save()
        
        messages.success(request, "Data lokal berhasil diperbarui!")
        return redirect('read_panenlokal')
            
    
def delete_panenlokal(request,id) :
    getdetailobj = models.detailpanenlokal.objects.get(iddetailpanen_lokal = id)
    getdetailobj.delete()
    messages.success(request, "Data berhasil dihapus!")
    return redirect('read_panenlokal')


'''READ AKUMULASI PENIMBANGAN'''
def read_penimbanganmitra(request) :
       
    detailobj = models.detailpanenmitra.objects.values('idpanen_mitra__id_mitra__nama_mitra','id_komoditas__nama_komoditas','idpanen_mitra__tanggal_panen','tanggal_kadaluwarsa').annotate(kuantitas_total = Sum('kuantitas'))

    return render(request,'panen/penimbangan/read_penimbanganmitra.html',{
        'penimbangan' : detailobj,
    })
    
def read_penimbanganlokal(request) :
   
    detailobj = models.detailpanenlokal.objects.values('id_komoditas__nama_komoditas','idpanen_lokal__tanggal_panen','tanggal_kadaluwarsa').annotate(kuantitas_total = Sum('kuantitas'))

    print(detailobj)
    return render(request,'panen/penimbangan/read_penimbanganlokal.html',{
        'penimbangan' : detailobj,
    })


'''CRUD JENIS BIAYA'''
def read_jenisbiaya(request) :
    biayaobj = models.jenisbiaya.objects.all()
    if not biayaobj.exists() :
        messages.error(request,"Data Jenis Biaya Tidak Ditemukan")
    
    return render(request,'biaya/jenis/read_jenisbiaya.html',{
        'biayaobj' : biayaobj
    })

def create_jenisbiaya(request) :
    if request.method == "GET" :
        return render(request, 
                      'biaya/jenis/create_jenisbiaya.html')
    else :
        jenis_biaya = request.POST["jenis_biaya"]
        biayaobj = models.jenisbiaya.objects.filter(jenis_biaya=jenis_biaya)
        
        if len(biayaobj) >0:
            messages.error(request,"Jenis Biaya Sudah Ada")
        else :
            models.jenisbiaya(
                jenis_biaya = jenis_biaya,
            ).save()

            messages.success(request,"Data Biaya Berhasil Ditambahkan!")

        return redirect("read_jenisbiaya")

def update_jenisbiaya(request,id) :
    try :
        getbiayaobj = models.jenisbiaya.objects.get(idjenisbiaya = id)
    except models.jenisbiaya.DoesNotExist :
        messages.error(request,"Jenis Biaya Tidak Ditemukan!")

    if request.method == "GET" :
        return render(request, 
                      'biaya/jenis/update_jenisbiaya.html',{
                          'biayaobj' : getbiayaobj
                      })
    else :
        jenis_biaya = request.POST["jenis_biaya"]
        print("jenis biaya :", jenis_biaya)
        if models.jenisbiaya.objects.filter(jenis_biaya=jenis_biaya).exclude(idjenisbiaya=id).exists():
            messages.error(request, "Nama Biaya Sudah Ada!")
            return redirect('read_jenisbiaya')
        
        getbiayaobj.jenis_biaya = jenis_biaya
        getbiayaobj.save()
        messages.success(request,"Data Biaya Berhasil Ditambahkan!")
        return redirect("read_jenisbiaya")

def delete_jenisbiaya(request,id) :
    getbiayaobj = models.jenisbiaya.objects.get(idjenisbiaya = id)
    getbiayaobj.delete()
    messages.success(request,"Data Berhasil Dihapus")
    return redirect('read_jenisbiaya')


'''CRUD DETAIL BIAYA'''
def read_detailbiaya(request) :
    biayaobj = models.biaya.objects.all()
    if not biayaobj.exists() :
        messages.error(request,"Data Biaya Tidak Ditemukan!")
    
   
    return render(request,'biaya/detail/read_detailbiaya.html',{
        'biayaobj' : biayaobj
    })

def create_detailbiaya(request) :
    alljenisbiaya = models.jenisbiaya.objects.all()
    if request.method == "GET" :
        return render(request,'biaya/detail/create_detailbiaya.html',{
            'alljenisbiaya' : alljenisbiaya
        })
    else :
        jenis_biaya = request.POST["jenis_biaya"]
        tanggal = request.POST['tanggal']
        nama_biaya = request.POST['nama_biaya']
        nominal_biaya = request.POST['nominal_biaya']

        jenisbiaya = models.jenisbiaya.objects.get(jenis_biaya=jenis_biaya)

        models.biaya(
            idjenisbiaya = jenisbiaya,
            tanggal = tanggal,
            nama_biaya = nama_biaya,
            nominal_biaya = nominal_biaya
        ).save()

        messages.success(request,"Data Biaya Berhasil Ditambahkan")
        return redirect("read_detailbiaya")
    
def update_detailbiaya(request, id):
    try:
        getdetailobj = models.biaya.objects.get(idbiaya=id)
        
    except models.biayaa.DoesNotExist:
        messages.error(request, "Data Biaya tidak ditemukan!")
        return redirect('read_detailbiaya')
  
    allbiayaobj = models.jenisbiaya.objects.all()
  
    if request.method == "GET":
        tanggal = getdetailobj.tanggal.strftime('%Y-%m-%d')  # Format tanggal
        return render(request, 'biaya/detail/update_detailbiaya.html', {
            'getdetailobj': getdetailobj,
            'allbiayaobj' : allbiayaobj,
            'tanggal': tanggal,
        })
    else:    
        getjenisbiaya = models.jenisbiaya.objects.get(jenis_biaya=request.POST["jenis_biaya"])
        

        getdetailobj.idjenisbiayaa = getjenisbiaya
        getdetailobj.tanggal = request.POST['tanggal']
        getdetailobj.nama_biaya = request.POST["nama_biaya"]
        getdetailobj.nominal_biaya = request.POST["nominal_biaya"]

        # getdetailobj.idjenisbiaya.jenis_biaya.save()
        getdetailobj.save()
        
        messages.success(request, "Data Detail Biaya berhasil diperbarui!")
        return redirect('read_detailbiaya')
    
def delete_detailbiaya(request,id) :
    getdetailobj = models.biaya.objects.get(idbiaya = id)
    getdetailobj.delete()
    messages.success(request,"Data Berhasil Dihapus!")
    return redirect('read_detailbiaya')


''' CRUD PRODUKSI'''
def read_produksi(request) :
    produksiobj = models.detailproduksi.objects.all()
    if not produksiobj.exists() :
        messages.error(request,"Data Produksi Tidak Ditemukan!")

    return render(request,"produksi/read_produksi.html",{
        'produksiobj' : produksiobj
    })

def create_produksi(request) :
    produkobj = models.produk.objects.all()
    if request.method == 'GET' :
        return render(request,"produksi/create_produksi.html",{
            'produkobj' : produkobj
        })
        
    else :
        tanggal = request.POST['tanggal']
        status_produk = request.POST.getlist('status_produk')
        produk = request.POST.getlist('produk')
        kuantitas = request.POST.getlist('kuantitas')


        produksi = models.produksi(
            tanggal=tanggal,
        )

        produksi.save()
        for status_produk,produk,kuantitas in zip(status_produk,produk,kuantitas) :
            models.detailproduksi(
                id_produk=models.produk.objects.get(id_produk = produk),
                id_produksi = produksi,
                kuantitas_produk = kuantitas,
                status_produk = status_produk
            ).save()
        
        messages.success(request,"Data Status Produk Berhasil Disimpan!")
        return redirect("read_produksi")
    
def update_produksi(request,id) :
    getproduksi = models.detailproduksi.objects.get(iddetail_produksi = id)
    produkobj = models.produk.objects.all()
    if request.method == 'GET' :
        tanggal =getproduksi.id_produksi.tanggal.strftime('%Y-%m-%d')
        return render(request,"produksi/update_produksi.html",{
            'getproduksi' : getproduksi,
            'produkobj' : produkobj,
            'tanggal' : tanggal
        })
    else :
        getproduk = models.produk.objects.get(id_produk = request.POST['produk'])

        getproduksi.id_produksi.tanggal = request.POST['tanggal']
        getproduksi.status_produk = request.POST['status_produk']
        getproduksi.id_produk = getproduk
        getproduksi.kuantitas_produk = request.POST['kuantitas']
        getproduksi.id_produksi.save()
        getproduksi.save()

        messages.success(request, "Data produksi berhasil diperbarui!")
        return redirect('read_produksi')
    
def delete_produksi(request,id) :
    getproduksi = models.detailproduksi.objects.get(iddetail_produksi = id)
    getproduksi.delete()
    messages.success(request, "Data produksi berhasil dihapus!")
    return redirect('read_produksi')


'''LAPORAN PANEN'''
def laporan_panen(request) :
    mulai = request.GET.get('mulai')
    akhir = request.GET.get('akhir')
    jenis_panen = request.GET.get('jenis_panen')
    if mulai and akhir  :
        mulai_date = datetime.strptime(mulai, "%Y-%m-%d")
        akhir_date = datetime.strptime(akhir, "%Y-%m-%d")
        if jenis_panen == 'panen lokal' :

            panenlokalobj = models.panenlokal.objects.filter(tanggal_panen__range = (mulai,akhir)).order_by('tanggal_panen')
            detailobjlokal = []
            listgrandtotal = []
            for item in panenlokalobj :
                listdetail = []
                listhargabeli = []
                idpanen_lokal = item.idpanen_lokal
            
                filterdetailpanen = models.detailpanenlokal.objects.filter(idpanen_lokal = idpanen_lokal)


                if not filterdetailpanen.exists() :
                    continue

                for i in filterdetailpanen :
                    hargapembelian = i.id_komoditas.harga_beli * i.kuantitas
                    print('harga beli' ,hargapembelian)
                    listhargabeli.append(hargapembelian)
                print(listhargabeli)
                totalbeli = sum(listhargabeli)
                listdetail.append(item)
                listdetail.append(filterdetailpanen)
                listdetail.append(listhargabeli)
                listdetail.append(totalbeli)

                listgrandtotal.append(totalbeli)
                detailobjlokal.append(listdetail)

            grandtotallokal = sum(listgrandtotal)
            print(listgrandtotal)
            print(grandtotallokal)
            print(detailobjlokal)
            return render(request,'laporan/laporan_panen.html',{
            'detailobjlokal' :detailobjlokal,
            'grandtotallokal' :grandtotallokal,
            'mulai' : mulai_date,
            'akhir' :akhir_date,
            'jenis_panen' : jenis_panen
        })
        else :
            panenmitraobj = models.panenmitra.objects.filter(tanggal_panen__range = (mulai,akhir)).order_by('tanggal_panen')
       
            detailobj = []
            listgrandtotal = []
            for item in panenmitraobj :
                listdetail = []
                listhargabeli = []
                idpanen_mitra = item.idpanen_mitra
            
                filterdetailpanen = models.detailpanenmitra.objects.filter(idpanen_mitra = idpanen_mitra)

                
                if not filterdetailpanen.exists() :
                    continue

                for i in filterdetailpanen :
                    hargapembelian = i.id_komoditas.harga_beli * i.kuantitas
                    print('harga beli' ,hargapembelian)
                    listhargabeli.append(hargapembelian)
                print(listhargabeli)
                totalbeli = sum(listhargabeli)
                listdetail.append(item)
                listdetail.append(filterdetailpanen)
                listdetail.append(listhargabeli)
                listdetail.append(totalbeli)

                listgrandtotal.append(totalbeli)
                detailobj.append(listdetail)


            grandtotal = sum(listgrandtotal)
            print(listgrandtotal)
            print(grandtotal)
            print(detailobj)

            return render(request,'laporan/laporan_panen.html',{
            'detailobj' :detailobj,
            'grandtotal' :grandtotal,
            'mulai' : mulai,
            'akhir' :akhir,
            'jenis_panen' : jenis_panen
        })
            
    else :
        if jenis_panen == 'panen lokal' :
            
            panenlokalobj = models.panenlokal.objects.all().order_by('tanggal_panen')
            detailobjlokal = []
            listgrandtotal = []
            for item in panenlokalobj :
                listdetail = []
                listhargabeli = []
                idpanen_lokal = item.idpanen_lokal
            
                filterdetailpanen = models.detailpanenlokal.objects.filter(idpanen_lokal = idpanen_lokal)

                
                if not filterdetailpanen.exists() :
                    continue

                for i in filterdetailpanen :
                    hargapembelian = i.id_komoditas.harga_beli * i.kuantitas
                    print('harga beli' ,hargapembelian)
                    listhargabeli.append(hargapembelian)
                totalbeli = sum(listhargabeli)
                listdetail.append(item)
                listdetail.append(filterdetailpanen)
                listdetail.append(listhargabeli)
                listdetail.append(totalbeli)

                listgrandtotal.append(totalbeli)
                detailobjlokal.append(listdetail)
            grandtotallokal = sum(listgrandtotal)
            print(listgrandtotal)
            print(grandtotallokal)
            print(detailobjlokal)

            return render(request,'laporan/laporan_panen.html',{
            'detailobjlokal' :detailobjlokal,
            'grandtotallokal' :grandtotallokal,
            'jenis_panen' : jenis_panen
        })
        else :
            jenis_panen = 'panen mitra'
            panenmitraobj = models.panenmitra.objects.all().order_by('tanggal_panen')
         
            detailobj = []
            listgrandtotal = []
            for item in panenmitraobj :
                
                listdetail = []
                listhargabeli = []
                idpanen_mitra = item.idpanen_mitra
                filterdetailpanen = models.detailpanenmitra.objects.filter(idpanen_mitra = idpanen_mitra)

                if not filterdetailpanen.exists() :
                    continue
                
                for i in filterdetailpanen :
                    hargapembelian = i.id_komoditas.harga_beli * i.kuantitas
                    print('harga beli' ,hargapembelian)
                    listhargabeli.append(hargapembelian)
                totalbeli = sum(listhargabeli)
                listdetail.append(item)
                listdetail.append(filterdetailpanen)
                listdetail.append(listhargabeli)
                listdetail.append(totalbeli)

                listgrandtotal.append(totalbeli)
                detailobj.append(listdetail)

            grandtotal = sum(listgrandtotal)
            print(listgrandtotal)
            print(grandtotal)
            print(detailobj)





            return render(request,'laporan/laporan_panen.html',{
                'detailobj' :detailobj,
                'grandtotal' :grandtotal,
                'jenis_panen' : jenis_panen
            })
    

# '''LAPORAN LABA RUGI'''
# def laporan_labarugi(request) :
#     if len(request.GET) == 0 :
#         return render(request,'laporan/laporan_labarugi.html') 
#     else :
#         bulan = request.GET['bulan']
#         print(bulan)
#         year, month = map(int, bulan.split('-'))
#         bulanaja = calendar.month_name[month]
#         tanggal_mulai = datetime(year, month, 1)
#         tanggal_akhir = datetime(year, month, calendar.monthrange(year, month)[1])
#         detailpenjualan = models.detailpenjualan.objects.filter(id_penjualan__tanggal__range = (tanggal_mulai,tanggal_akhir))
        
        

#         if not detailpenjualan.exists() :
#             messages.error(request, "Data Penjualan tidak ditemukan!")
#             return redirect('laporan_labarugi')
        


#         listtotaljual = []
#         listhpptemp = []
#         wip_awal = {}
#         wip_akhir = {}  
#         fg_awal = {}
#         fg_akhir = {}  
#         for item in detailpenjualan :
#             # Pendapatan awal
#             kuantitask = item.kuantitas_komoditas
#             kuantitasp = item.kuantitas_produk
#             hargak = item.id_komoditas.harga_jual
#             hargap = item.id_produk.harga_produk
        
#             total = kuantitask*hargak + kuantitasp*hargap
#             listtotaljual.append(total)

#             # HPP(produksi)
#             nama_produk = item.id_produk.nama_produk
#             nama_komoditas = konversi_produk_to_komoditas[nama_produk][0]
#             hargakomoditas = models.komoditas.objects.filter(nama_komoditas=nama_komoditas).filter(id_grade__nama_grade = 'olah').values('harga_beli')

#             print("harga",hargakomoditas)
#             print(nama_produk)
#             konversiproduk = konversi_produk_to_komoditas[nama_produk][1]
#             print(konversiproduk)

#             hasilkonv = math.ceil(kuantitasp*konversiproduk)
#             print(hasilkonv)
            
#             filterwipawal = models.detailproduksi.objects.filter(id_produk__nama_produk=nama_produk).filter(status_produk = 'wip').filter(id_produksi__tanggal = tanggal_mulai)

#             filterwipakhir = models.detailproduksi.objects.filter(id_produk__nama_produk=nama_produk).filter(status_produk = 'wip').filter(id_produksi__tanggal = tanggal_akhir)

#             filterfgawal = models.detailproduksi.objects.filter(id_produk__nama_produk=nama_produk).filter(status_produk = 'fg').filter(id_produksi__tanggal = tanggal_mulai)

#             filterfgakhir = models.detailproduksi.objects.filter(id_produk__nama_produk=nama_produk).filter(status_produk = 'fg').filter(id_produksi__tanggal = tanggal_akhir)

#             print(filterwipawal,filterwipakhir)

#             # wip awal
#             for i in filterwipawal:
#                 harga = i.kuantitas_produk * i.id_produk.harga_produk
#                 nama_produk = i.id_produk.nama_produk
#                 if nama_produk in wip_awal:
#                     wip_awal[nama_produk] += harga
#                 else:
#                     wip_awal[nama_produk] = harga

#             # wip akhir
#             for i in filterwipakhir:
#                 harga = i.kuantitas_produk * i.id_produk.harga_produk
#                 nama_produk = i.id_produk.nama_produk
#                 if nama_produk in wip_akhir:
#                     wip_akhir[nama_produk] += harga
#                 else:
#                     wip_akhir[nama_produk] = harga
           
#             # fg awal
#             for i in filterfgawal:
#                 harga = i.kuantitas_produk * i.id_produk.harga_produk
#                 nama_produk = i.id_produk.nama_produk
#                 if nama_produk in fg_awal:
#                     fg_awal[nama_produk] += harga
#                 else:
#                     fg_awal[nama_produk] = harga

#             # fg akhir
#             for i in filterfgakhir:
#                 harga = i.kuantitas_produk * i.id_produk.harga_produk
#                 nama_produk = i.id_produk.nama_produk
#                 if nama_produk in fg_akhir:
#                     fg_akhir[nama_produk] += harga
#                 else:
#                     fg_akhir[nama_produk] = harga

           

#             hargawipawal = wip_awal.get(nama_produk, 0)
#             hargawipakhir = wip_akhir.get(nama_produk, 0)

#             hpp_temporary = (hasilkonv * hargakomoditas[0]['harga_beli']) + hargawipawal - hargawipakhir
#             listhpptemp.append(hpp_temporary)
#             print('hpp smntara', hpp_temporary)



        
#         tenagakerja_dan_overhead = models.biaya.objects.filter(
#             Q(idjenisbiaya__jenis_biaya='Biaya Tenaga Kerja') | 
#             Q(idjenisbiaya__jenis_biaya='Biaya Overhead'),
#             tanggal__range=(tanggal_mulai, tanggal_akhir))
#         total_biaya = tenagakerja_dan_overhead.aggregate(total_biaya=Sum('nominal_biaya'))

#         hpp_final = sum(listhpptemp) + total_biaya['total_biaya']

        
#         listfgawal = []
#         for i in fg_awal.values() :
#             listfgawal.append(i)

#         listfgakhir = []
#         for i in fg_akhir.values() :
#             listfgakhir.append(i)

        
#         filterkom = models.komoditas.objects.exclude(id_grade__nama_grade = 'olah')

        
#         listmitra = []
#         listlokal = []
#         # Harga Beli Komoditas
#         for item in filterkom :
#             id_kom = item
#             print('id komoditas',id_kom)

#             detailmitra = models.detailpanenmitra.objects.filter(id_komoditas=id_kom)
#             detaillokal = models.detailpanenlokal.objects.filter(id_komoditas=id_kom)

#             for a in detailmitra :
#                 hargakomoditas = a.kuantitas * a.id_komoditas.harga_beli
#                 listmitra.append(hargakomoditas)

#             for b in detaillokal :
#                 hargakomoditas = b.kuantitas * b.id_komoditas.harga_beli
#                 listlokal.append(hargakomoditas)

#         # HPP Penjualan
#         hppembelian = hpp_final+sum(listmitra)+sum(listlokal) + sum(listfgawal) - sum(listfgakhir)

#         # Pendapatan Kotor
#         totalpendapatanawal = sum(listtotaljual)
#         laba_kotor = totalpendapatanawal- hppembelian

#         # Pajak Penghasilan
#         pajak_penghasilan = (0.5/100) * laba_kotor

       
#         bbu = models.biaya.objects.filter(tanggal__range=(tanggal_mulai,tanggal_akhir)).filter(idjenisbiaya__jenis_biaya ='Beban Usaha')
#         print('dict',bbu)
#         dictbbu = {}
#         for item in bbu :
#             namabiaya = item.nama_biaya
#             if namabiaya in dictbbu :
#                 dictbbu[namabiaya] += item.nominal_biaya
#             else :
#                 dictbbu[namabiaya] = item.nominal_biaya

    
    

#         bbufix = 0
#         for item in dictbbu.values():
#             bbufix+=item
      
#         # Pendapatan bersih
#         pendapatan_bersih = laba_kotor-pajak_penghasilan-bbufix


#         return render(
#             request,'laporan/laporan_labarugi.html',{
#                 'bulan':bulan,
#                 'month':bulanaja,
#                 'tanggal_mulai':tanggal_mulai,
#                 'tanggal_akhir':tanggal_akhir,
#                 'pendapatan_awal' :totalpendapatanawal,
#                 'hpproduksi' : hpp_final,
#                 'hppenjualan' : hppembelian,
#                 'laba_kotor' :laba_kotor,
#                 'pajak_penghasilan' : pajak_penghasilan,
#                 'dictbbu' : dictbbu,
#                 'bbufix' : bbufix,
#                 'pendapatan_bersih' : pendapatan_bersih
#             }
#         )

'''LAPORAN LABA RUGI'''
def laporan_labarugi(request) :
    if len(request.GET) == 0 :
        return render(request,'laporan/laporan_labarugi.html') 
    else :
        bulan = request.GET['bulan']
        print(bulan)
        year, month = map(int, bulan.split('-'))
        bulanaja = calendar.month_name[month]
        bulan_fix = bulan_indo[bulanaja]
        print('bulan fix',bulan_fix)
        tanggal_mulai = datetime(year, month, 1)
        tanggal_akhir = datetime(year, month, calendar.monthrange(year, month)[1])

     


        detailpenjualan = models.detailpenjualan.objects.filter(id_penjualan__tanggal__range = (tanggal_mulai,tanggal_akhir))

        if not detailpenjualan.exists() :
            messages.error(request, "Data Penjualan tidak ditemukan!")
            return redirect('laporan_labarugi')
    
        listtotaljual = []
        listhpptemp = []
        wip_awal = {}
        wip_akhir = {}  
        fg_awal = {}
        fg_akhir = {}  
        for item in detailpenjualan :
            # Pendapatan awal
            kuantitask = item.kuantitas_komoditas
            kuantitasp = item.kuantitas_produk
            hargak = item.id_komoditas.harga_jual
            hargap = item.id_produk.harga_produk
        
            total = kuantitask*hargak + kuantitasp*hargap
            listtotaljual.append(total)

        # HPP(produksi)
        produkobj = models.produk.objects.all()
        for i in produkobj :  
            nama_produk = i.nama_produk

            nama_komoditas = konversi_produk_to_komoditas[nama_produk][0]
            
            hargakomoditas = models.komoditas.objects.filter(nama_komoditas=nama_komoditas).filter(id_grade__nama_grade = 'olah').values('harga_beli')

        
            konversiproduk = konversi_produk_to_komoditas[nama_produk][1]
            print(konversiproduk)

            filterfgall = models.detailproduksi.objects.filter(id_produk__nama_produk=nama_produk,status_produk = 'fg')
    
            for a in filterfgall :
                kuantitasprod = a.kuantitas_produk
                hasilkonv = math.ceil(kuantitasprod*konversiproduk)
            
            filterwipawal = models.detailproduksi.objects.filter(id_produk__nama_produk=nama_produk).filter(status_produk = 'wip').filter(id_produksi__tanggal = tanggal_mulai)

            filterwipakhir = models.detailproduksi.objects.filter(id_produk__nama_produk=nama_produk).filter(status_produk = 'wip').filter(id_produksi__tanggal = tanggal_akhir)

            filterfgawal = models.detailproduksi.objects.filter(id_produk__nama_produk=nama_produk).filter(status_produk = 'fg').filter(id_produksi__tanggal = tanggal_mulai)

            filterfgakhir = models.detailproduksi.objects.filter(id_produk__nama_produk=nama_produk).filter(status_produk = 'fg').filter(id_produksi__tanggal = tanggal_akhir)


            # wip awal
            for b in filterwipawal:
                harga = b.kuantitas_produk * b.id_produk.harga_produk
                nama_produk = b.id_produk.nama_produk
                if nama_produk in wip_awal:
                    wip_awal[nama_produk] += harga
                else:
                    wip_awal[nama_produk] = harga

            # wip akhir
            for b in filterwipakhir:
                harga = b.kuantitas_produk * b.id_produk.harga_produk
                nama_produk = b.id_produk.nama_produk
                if nama_produk in wip_akhir:
                    wip_akhir[nama_produk] += harga
                else:
                    wip_akhir[nama_produk] = harga
        
            # fg awal
            for b in filterfgawal:
                harga = b.kuantitas_produk * b.id_produk.harga_produk
                nama_produk = b.id_produk.nama_produk
                if nama_produk in fg_awal:
                    fg_awal[nama_produk] += harga
                else:
                    fg_awal[nama_produk] = harga

            # fg akhir
            for b in filterfgakhir:
                harga = b.kuantitas_produk * b.id_produk.harga_produk
                nama_produk = b.id_produk.nama_produk
                if nama_produk in fg_akhir:
                    fg_akhir[nama_produk] += harga
                else:
                    fg_akhir[nama_produk] = harga

        

            hargawipawal = wip_awal.get(nama_produk, 0)
            hargawipakhir = wip_akhir.get(nama_produk, 0)

            hpp_temporary = (hasilkonv * hargakomoditas[0]['harga_beli']) + hargawipawal - hargawipakhir
            listhpptemp.append(hpp_temporary)

        tenagakerja_dan_overhead = models.biaya.objects.filter(
            Q(idjenisbiaya__jenis_biaya='Biaya Tenaga Kerja') | 
            Q(idjenisbiaya__jenis_biaya='Biaya Overhead'),
            tanggal__range=(tanggal_mulai, tanggal_akhir))
        total_biaya = tenagakerja_dan_overhead.aggregate(total_biaya=Sum('nominal_biaya'))

        hpp_final = sum(listhpptemp) + total_biaya['total_biaya']

        
        listfgawal = []
        for i in fg_awal.values() :
            listfgawal.append(i)

        listfgakhir = []
        for i in fg_akhir.values() :
            listfgakhir.append(i)

        
        filterkom = models.komoditas.objects.exclude(id_grade__nama_grade = 'olah')

        
        listmitra = []
        listlokal = []
        # Harga Beli Komoditas
        for item in filterkom :
            id_kom = item
            print('id komoditas',id_kom)

            detailmitra = models.detailpanenmitra.objects.filter(id_komoditas=id_kom)
            detaillokal = models.detailpanenlokal.objects.filter(id_komoditas=id_kom)

            for a in detailmitra :
                hargakomoditas = a.kuantitas * a.id_komoditas.harga_beli
                listmitra.append(hargakomoditas)

            for b in detaillokal :
                hargakomoditas = b.kuantitas * b.id_komoditas.harga_beli
                listlokal.append(hargakomoditas)

        # HPP Penjualan
        hppembelian = hpp_final+sum(listmitra)+sum(listlokal) + sum(listfgawal) - sum(listfgakhir)

        # Pendapatan Kotor
        totalpendapatanawal = sum(listtotaljual)
        laba_kotor = totalpendapatanawal- hppembelian

        # Pajak Penghasilan
        pajak_penghasilan = (0.5/100) * laba_kotor

       
        bbu = models.biaya.objects.filter(tanggal__range=(tanggal_mulai,tanggal_akhir)).filter(idjenisbiaya__jenis_biaya ='Beban Usaha')
        print('dict',bbu)
        dictbbu = {}
        for item in bbu :
            namabiaya = item.nama_biaya
            if namabiaya in dictbbu :
                dictbbu[namabiaya] += item.nominal_biaya
            else :
                dictbbu[namabiaya] = item.nominal_biaya

    
    

        bbufix = 0
        for item in dictbbu.values():
            bbufix+=item
      
        # Pendapatan bersih
        pendapatan_bersih = laba_kotor-pajak_penghasilan-bbufix


        return render(
            request,'laporan/laporan_labarugi.html',{
                'bulan':bulan,
                'month':bulan_fix,
                'tanggal_mulai':tanggal_mulai,
                'tanggal_akhir':tanggal_akhir,
                'pendapatan_awal' :totalpendapatanawal,
                'hpproduksi' : hpp_final,
                'hppenjualan' : hppembelian,
                'laba_kotor' :laba_kotor,
                'pajak_penghasilan' : pajak_penghasilan,
                'dictbbu' : dictbbu,
                'bbufix' : bbufix,
                'pendapatan_bersih' : pendapatan_bersih
            }
        )
        
       
        
        
        
        

