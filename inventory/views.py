from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Product
from .forms import ProductForm
import csv
from django.http import HttpResponse
from django.contrib import messages
from io import TextIOWrapper
from .models import Product

@login_required
def product_list(request):
    products = Product.objects.filter(owner=request.user)
    return render(request, 'inventory/product_list.html', {'products': products})

@login_required
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save(commit=False)
            product.owner = request.user
            product.save()
            messages.success(request, 'Product added successfully!')
            return redirect('product_list')
    else:
        form = ProductForm()
    return render(request, 'inventory/add_product.html', {'form': form})

@login_required
def edit_product(request, pk):
    product = get_object_or_404(Product, pk=pk, owner=request.user)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product updated successfully!')
            return redirect('product_list')
    else:
        form = ProductForm(instance=product)
    return render(request, 'inventory/edit_product.html', {'form': form})

@login_required
def delete_product(request, pk):
    product = get_object_or_404(Product, pk=pk, owner=request.user)
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Product deleted successfully!')
        return redirect('product_list')
    return render(request, 'inventory/delete_product.html', {'product': product})

@login_required
def import_products(request):
    if request.method == 'POST' and request.FILES['csv_file']:
        csv_file = TextIOWrapper(request.FILES['csv_file'].file, encoding='utf-8')
        reader = csv.DictReader(csv_file)
        
        imported = 0
        for row in reader:
            try:
                Product.objects.create(
                    name=row['name'],
                    description=row['description'],
                    price=row['price'],
                    quantity=row['quantity'],
                    owner=request.user
                )
                imported += 1
            except Exception as e:
                messages.error(request, f"Error importing row: {row}. Error: {str(e)}")
        
        messages.success(request, f'Successfully imported {imported} products!')
        return redirect('product_list')
    return render(request, 'inventory/import_products.html')

@login_required
def export_products(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="products.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['name', 'description', 'price', 'quantity', 'created_at'])
    
    products = Product.objects.filter(owner=request.user)
    for product in products:
        writer.writerow([
            product.name,
            product.description,
            product.price,
            product.quantity,
            product.created_at.strftime('%Y-%m-%d %H:%M:%S')
        ])
    
    return response
    