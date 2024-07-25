from django.urls import path
from . import views

urlpatterns = [
    # CRUD MITRA
    path('create_mitra', views.create_mitra,name='create_mitra'),
    path('read_mitra/', views.read_mitra,name='read_mitra'),
    path('update_mitra/<str:id>', views.update_mitra,name='update_mitra'),
    path('delete_mitra/<str:id>', views.delete_mitra,name='delete_mitra'),
    # CRUD PENJUALAN
    path('create_penjualan', views.create_penjualan,name='create_penjualan'),
    path('read_penjualan', views.read_penjualan,name='read_penjualan'),
    path('update_penjualan/<str:id>', views.update_penjualan,name='update_penjualan'),
    path('delete_penjualan/<str:id>', views.delete_penjualan,name='delete_penjualan'),
    # CRUD PANEN
    path('create_panenmitra', views.create_panenmitra,name='create_panenmitra'),
    path('read_panenmitra', views.read_panenmitra,name='read_panenmitra'),
    path('update_panenmitra/<str:id>', views.update_panenmitra,name='update_panenmitra'),
    path('delete_panenmitra/<str:id>', views.delete_panenmitra,name='delete_panenmitra'),
    
    path('create_panenlokal', views.create_panenlokal,name='create_panenlokal'),
    path('read_panenlokal', views.read_panenlokal,name='read_panenlokal'),
    path('update_panenlokal/<str:id>', views.update_panenlokal,name='update_panenlokal'),
    path('delete_panenlokal/<str:id>', views.delete_panenlokal,name='delete_panenlokal'),

    path('read_penimbanganmitra', views.read_penimbanganmitra,name='read_penimbanganmitra'),
    path('read_penimbanganlokal', views.read_penimbanganlokal,name='read_penimbanganlokal'),

    # CRUD BIAYA
    path('create_jenisbiaya', views.create_jenisbiaya,name='create_jenisbiaya'),
    path('read_jenisbiaya', views.read_jenisbiaya,name='read_jenisbiaya'),
    path('update_jenisbiaya/<str:id>', views.update_jenisbiaya,name='update_jenisbiaya'),
    path('delete_jenisbiaya/<str:id>', views.delete_jenisbiaya,name='delete_jenisbiaya'),
    
    path('create_detailbiaya', views.create_detailbiaya,name='create_detailbiaya'),
    path('read_detailbiaya', views.read_detailbiaya,name='read_detailbiaya'),
    path('update_detailbiaya/<str:id>', views.update_detailbiaya,name='update_detailbiaya'),
    path('delete_detailbiaya/<str:id>', views.delete_detailbiaya,name='delete_detailbiaya'),

    # CRUD PRODUKSI
    path('create_produksi', views.create_produksi,name='create_produksi'),
    path('read_produksi', views.read_produksi,name='read_produksi'),
    path('update_produksi/<str:id>', views.update_produksi,name='update_produksi'),
    path('delete_produksi/<str:id>', views.delete_produksi,name='delete_produksi'),

    # LAPORAN PANEN
    path('laporan_panen/', views.laporan_panen,name='laporan_panen'),

    # LAPORAN labarugi
    path('laporan_labarugi', views.laporan_labarugi,name='laporan_labarugi'),
    
]