from decimal import *

from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.core.mail import EmailMessage
from django.db.models import Sum
from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import get_object_or_404
from django.template.loader import get_template
from rest_framework.response import Response
from rest_framework.views import APIView
from .forms import *
from .models import *
from .serializers import CustomerSerializer

# email

now = timezone.now()


def home(request):
    return render(request, 'portfolio/home.html',
                  {'portfolio': home})


@login_required
def customer_list(request):
    customer = Customer.objects.filter(created_date__lte=timezone.now())
    return render(request, 'portfolio/customer_list.html',
                  {'customers': customer})


def register(request):
    print("entered into register view method")
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return render(request,
                          'registration/registerdone.html',
                          {'form': form})
    else:
        form = RegisterForm()
    return render(request, "registration/register.html", {"form": form})


@login_required
def customer_edit(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == "POST":
        # update
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            customer = form.save(commit=False)
            customer.updated_date = timezone.now()
            customer.save()
            customer = Customer.objects.filter(created_date__lte=timezone.now())
            return render(request, 'portfolio/customer_list.html',
                          {'customers': customer})
    else:
        # edit
        form = CustomerForm(instance=customer)
    return render(request, 'portfolio/customer_edit.html', {'form': form})


@login_required
def customer_delete(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    customer.delete()
    return redirect('portfolio:customer_list')


@login_required
def stock_list(request):
    stocks = Stock.objects.filter(purchase_date__lte=timezone.now())
    return render(request, 'portfolio/stock_list.html', {'stocks': stocks})


@login_required
def stock_new(request):
    if request.method == "POST":
        form = StockForm(request.POST)
        if form.is_valid():
            stock = form.save(commit=False)
            stock.created_date = timezone.now()
            stock.save()
            stocks = Stock.objects.filter(purchase_date__lte=timezone.now())
            return render(request, 'portfolio/stock_list.html',
                          {'stocks': stocks})
    else:
        form = StockForm()
        # print("Else")
    return render(request, 'portfolio/stock_new.html', {'form': form})


@login_required
def stock_edit(request, pk):
    stock = get_object_or_404(Stock, pk=pk)
    if request.method == "POST":
        form = StockForm(request.POST, instance=stock)
        if form.is_valid():
            stock = form.save()
            # stock.customer = stock.id
            stock.updated_date = timezone.now()
            stock.save()
            stocks = Stock.objects.filter(purchase_date__lte=timezone.now())
            return render(request, 'portfolio/stock_list.html', {'stocks': stocks})
    else:
        # print("else")
        form = StockForm(instance=stock)
    return render(request, 'portfolio/stock_edit.html', {'form': form})


@login_required
def stock_delete(request, pk):
    stock = get_object_or_404(Stock, pk=pk)
    stock.delete()
    return redirect('portfolio:stock_list')


@login_required
def investment_list(request):
    investments = Investment.objects.filter(acquired_date__lte=timezone.now())
    return render(request, 'portfolio/investment_list.html', {'investments': investments})


@login_required
def investment_new(request):
    if request.method == "POST":
        form = InvestmentForm(request.POST)
        if form.is_valid():
            investment = form.save(commit=False)
            investment.created_date = timezone.now()
            investment.save()
            investments = Investment.objects.filter(acquired_date__lte=timezone.now())
            return render(request, 'portfolio/investment_list.html',
                          {'investments': investments})
    else:
        form = InvestmentForm()
        # print("Else")
    return render(request, 'portfolio/investment_new.html', {'form': form})


@login_required
def investment_edit(request, pk):
    investment = get_object_or_404(Investment, pk=pk)
    if request.method == "POST":
        form = InvestmentForm(request.POST, instance=investment)
        if form.is_valid():
            investment = form.save()
            # stock.customer = stock.id
            investment.updated_date = timezone.now()
            investment.save()
            investments = Investment.objects.filter(acquired_date__lte=timezone.now())
            return render(request, 'portfolio/investment_list.html', {'investments': investments})
    else:
        # print("else")
        form = InvestmentForm(instance=investment)
    return render(request, 'portfolio/investment_edit.html', {'form': form})


@login_required
def investment_delete(request, pk):
    investment = get_object_or_404(Investment, pk=pk)
    investment.delete()
    return redirect('portfolio:investment_list')


@login_required
def portfolio(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    customers = Customer.objects.filter(created_date__lte=timezone.now())
    investments = Investment.objects.filter(customer=pk)
    stocks = Stock.objects.filter(customer=pk)

    sum_recent_value = Investment.objects.filter(customer=pk).aggregate(Sum('recent_value'))
    # print("sum_recent_value: " + str(sum_recent_value))

    sum_acquired_value = Investment.objects.filter(customer=pk).aggregate(Sum('acquired_value'))
    # print("sum_acquired_value: " + str(sum_acquired_value))

    # overall_investment_results = sum_recent_value - sum_acquired_value
    overall_investment_results = sum_recent_value['recent_value__sum'] - sum_acquired_value['acquired_value__sum']
    # overall_investment_results = Decimal(sum_recent_value['recent_value__sum']) - Decimal(sum_acquired_value['acquired_value__sum'])
    # print(" overall_investment_results:" + str(overall_investment_results))

    # Initialize the value of the stocks
    sum_current_stocks_value = 0
    sum_of_initial_stock_value = 0

    # Loop through each stock and add the value to the total
    for stock in stocks:
        sum_current_stocks_value += stock.current_stock_value()
        # print(type((stock.current_stock_value())))
        sum_of_initial_stock_value += stock.initial_stock_value()
        # print(type(int(stock.initial_stock_value())))

    overall_stocks_results = Decimal(sum_current_stocks_value) - Decimal(sum_of_initial_stock_value)
    # print(overall_stocks_results)

    return render(request, 'portfolio/portfolio.html', {'customers': customer,
                                                        'investments': investments,
                                                        'stocks': stocks,
                                                        'sum_acquired_value': sum_acquired_value[
                                                            'acquired_value__sum'],
                                                        'sum_recent_value': sum_recent_value[
                                                            'recent_value__sum'],
                                                        'sum_current_stocks_value': sum_current_stocks_value,
                                                        'sum_of_initial_stock_value': sum_of_initial_stock_value,
                                                        'overall_investment_results': overall_investment_results,
                                                        'overall_stocks_results': overall_stocks_results, })


class CustomerList(APIView):

    def get(self, request):
        customers_json = Customer.objects.all()
        serializer = CustomerSerializer(customers_json, many=True)
        return Response(serializer.data)


def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            return redirect('portfolio:home')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'registration/password_change_form.html', {
        'form': form
    })


from portfolio.utils import render_to_pdf


@login_required()
def portfolio_pdf(request, pk):
    template = get_template('portfolio/customer_portfolio_pdf.html')
    customer = get_object_or_404(Customer, pk=pk)
    customers = Customer.objects.filter(created_date__lte=timezone.now())
    investments = Investment.objects.filter(customer=pk)
    stocks = Stock.objects.filter(customer=pk)

    sum_recent_value = Investment.objects.filter(customer=pk).aggregate(Sum('recent_value'))
    print("sum_recent_value: " + str(sum_recent_value))
    sum_acquired_value = Investment.objects.filter(customer=pk).aggregate(Sum('acquired_value'))
    print("sum_acquired_value: " + str(sum_acquired_value))
    overall_investment_results = sum_recent_value['recent_value__sum'] - sum_acquired_value['acquired_value__sum']
    print(" overall_investment_results:" + str(overall_investment_results))
    # Initialize the value of the stocks
    sum_current_stocks_value = 0
    sum_of_initial_stock_value = 0

    # Loop through each stock and add the value to the total
    for stock in stocks:
        sum_current_stocks_value += stock.current_stock_value()
        print(type((stock.current_stock_value())))
        print("sum_current_stocks_value " + str(sum_current_stocks_value))
        sum_of_initial_stock_value += stock.initial_stock_value()
        print(type(int(stock.initial_stock_value())))
        print("sum_of_initial_stock_value " + str(sum_of_initial_stock_value))

        overall_stocks_results = float(sum_current_stocks_value) - float(sum_of_initial_stock_value)
        print("overall_stocks_results" + str(overall_stocks_results))
        context = {'customers': customer,
                   'investments': investments,
                   'stocks': stocks,
                   'sum_acquired_value': sum_acquired_value['acquired_value__sum'],
                   'sum_recent_value': sum_recent_value['recent_value__sum'],
                   'sum_current_stocks_value': sum_current_stocks_value,
                   'sum_of_initial_stock_value': sum_of_initial_stock_value,
                   'overall_investment_results': overall_investment_results,
                   'overall_stocks_results': overall_stocks_results,
                   }
        html = template.render(context)
        pdf = render_to_pdf('portfolio/customer_portfolio_pdf.html', context)
        if pdf:
            response = HttpResponse(pdf, content_type='application/pdf')
            filename = 'Portfolio_' + str(customer.name) + '.pdf'
            content = "inline; filename='%s'" % filename
            download = request.GET.get("download")
            if download:
                content = "attachment; filename='%s'" % filename
                response['Content-Disposition'] = content
            return response
        return HttpResponseNotFound("not found")


@login_required
def generate_portfolio_pdf(request, pk, context):
    customer = get_object_or_404(Customer, pk=pk)
    template = get_template('portfolio/customer_portfolio_pdf.html')

    html = template.render(context)
    pdf = render_to_pdf('portfolio/customer_portfolio_pdf.html', context)
    if pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'filename= "Portfolio_{}.pdf"'.format(customer.name)
        # return response
        # return HttpResponse(pdf, content_type='application/octet-stream')
        return pdf
    return HttpResponse("Not Found")


def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
           # myfile = request.FILES['file']
           # fs = FileSystemStorage.save()
            #filename = fs.save()
            subject = form.cleaned_data.get('subject')
            from_email = form.cleaned_data.get('from_email')
            message = form.cleaned_data.get('message')
            name = form.cleaned_data.get('name')

            message_format = "{0} has sent you a new message:\n\n{1}".format(name, message)

            msg = EmailMessage(
                subject,
                message_format,
                to=['sadhamisha20213@gmail.com'],
                from_email=from_email
            )



            msg.send()



            return render(request, 'contact_success.html')


    else:
        form = ContactForm()

    return render(request, 'contact.html', {'form': form})


from django.shortcuts import render, redirect
from django.core.files.storage import FileSystemStorage

def changed_password(request):
    form = PasswordChangeForm(user=request.user, data=request.POST)
    if request.method == 'GET':
        return render(request, "registration/password_change_form.html", {"form": form})
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return render(
                request, "registration/password_reset_done.html", {}
            )
        return render(
            request, "registration/password_change_form.html", {"errors": form.errors})