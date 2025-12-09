from datetime import date
from math import ceil
import json

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods

from .models import Contact, OrderUpdate, Orders, Product

# Lightweight seasonal intent mapper to mimic an AI recommender without an external API.
SEASON_KEYWORDS = {
    "christmas": ["christmas", "holiday", "santa", "gift", "winter", "snow"],
    "holiday": ["holiday", "gift", "family", "cozy"],
    "spring": ["spring", "easter", "fresh", "floral", "garden"],
    "summer": ["summer", "sun", "beach", "travel", "outdoor"],
    "fall": ["fall", "autumn", "harvest", "pumpkin", "warm"],
}


def current_season(today=None):
    """Map the current month to a loose seasonal theme."""
    now = today or date.today()
    if now.month == 12:
        return "christmas"
    if now.month in (11,):
        return "holiday"
    if now.month in (3, 4, 5):
        return "spring"
    if now.month in (6, 7, 8):
        return "summer"
    if now.month in (9, 10):
        return "fall"
    return "holiday"


def score_product_for_message(product, message, season):
    """Heuristic ranker: bump score when product text overlaps user intent or season."""
    text = f"{product.product_name} {product.desc} {product.category} {product.subcategory}".lower()
    user_terms = [t for t in message.lower().split() if t]
    keywords = SEASON_KEYWORDS.get(season, [])
    score = 0
    for kw in keywords:
        if kw in text:
            score += 3
    for term in user_terms:
        if term in text:
            score += 2
    # Freshness gives a small boost.
    if hasattr(product, "pub_date") and product.pub_date:
        if product.pub_date.month == date.today().month:
            score += 1
    return score


def build_recommendations(message):
    season = current_season()
    products = Product.objects.all()
    scored = []
    for product in products:
        scored.append((score_product_for_message(product, message, season), product))
    scored.sort(key=lambda pair: pair[0], reverse=True)
    top = [p for score, p in scored if score > 0][:5]
    if not top:
        top = [p for _, p in scored[:5]]
    payload = []
    for product in top:
        image_url = ""
        try:
            image_url = product.image.url
        except Exception:
            image_url = ""
        payload.append(
            {
                "id": product.id,
                "name": product.product_name,
                "price": product.price,
                "category": product.category,
                "desc": product.desc,
                "image": image_url,
            }
        )
    intro = "Christmas deals" if season == "christmas" else f"{season.title()} picks"
    reply = (
        f"{intro} coming right up! I looked for matches to your request "
        f"and highlighted {len(payload)} items you might like."
        if payload
        else "I could not find seasonal matches yet, but new items will appear here once added."
    )
    return season, reply, payload


@require_http_methods(["GET", "POST"])
def recommend_chatbot(request):
    if request.method == "GET":
        return render(
            request,
            "shopping/chatbot.html",
            {"season": current_season().title()},
        )

    try:
        data = json.loads(request.body.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        data = {}
    user_message = data.get("message", "").strip()
    season, reply, recommendations = build_recommendations(user_message)
    return JsonResponse(
        {
            "season": season,
            "reply": reply,
            "items": recommendations,
        }
    )


def index(request):
    featured = Product.objects.all()[:6]
    return render(request, 'shopping/index.html', {"featured": featured})


def all_products(request):
    products = Product.objects.all()
    return render(request, 'shopping/all_products.html', {"products": products})


def about(request):
    return render(request,'shopping/about.html')

def contact(request):
    thank=False
    if request.method=="POST":
        print(request)
        name=request.POST.get('name', '')
        email=request.POST.get('email', '')
        phone=request.POST.get('phone', '')
        desc=request.POST.get('desc', '')
        contact = Contact(name=name, email=email, phone=phone, desc=desc)
        contact.save()
        thank=True
    return render(request, "shopping/contact.html")

def tracker(request):
    if request.method=="POST":
        orderId = request.POST.get('orderId', '')
        email = request.POST.get('email', '')
        try:
            order = Orders.objects.filter(order_id=orderId, email=email)
            if len(order)>0:
                update = OrderUpdate.objects.filter(order_id=orderId)
                updates = []
                for item in update:
                    updates.append({'text': item.update_desc, 'time': item.timestamp})
                    response = json.dumps({"status":"success", "updates": updates, "itemsJson": order[0].items_json}, default=str)
                return HttpResponse(response)
            else:
                return HttpResponse('{"status":"noitem"}')
        except Exception as e:
            return HttpResponse('{"status":"error"}')

    return render(request, 'shopping/tracker.html')

def searchMatch(query, item):
    '''return true only if query matches the item'''
    if query in item.desc.lower() or query in item.product_name.lower() or query in item.category.lower():
        return True
    else:
        return False

def search(request):
    query = request.GET.get('search')
    display_query = (query or "").title()
    products = []
    if query:
        products = [
            item for item in Product.objects.all()
            if searchMatch(query.lower(), item)
        ]
    msg = ""
    if query and len(query) < 4:
        msg = "Please make sure to enter relevant search query"
    elif query and len(products) == 0:
        msg = f"Sorry, we couldn't find results for '{display_query}'."
    params = {'products': products, "msg": msg, "query": display_query}
    return render(request, 'shopping/search.html', params)

def productView(request, myid):
    #Fetching the product using the id
    product=Product.objects.filter(id=myid)
    print(product)
    return render(request, "shopping/prodView.html", {'product':product[0]})

def checkout(request):
    if request.method=="POST":
        items_json = request.POST.get('itemsJson', '')
        name = request.POST.get('name', '')
        amount = request.POST.get('amount', '')
        email = request.POST.get('email', '')
        address = request.POST.get('address1', '') + " " + request.POST.get('address2', '')
        city = request.POST.get('city', '')
        state = request.POST.get('state', '')
        pin_code = request.POST.get('pin_code', '')
        phone = request.POST.get('phone', '')
        order = Orders(items_json=items_json, name=name, email=email, address=address, city=city,
                       state=state, pin_code=pin_code, phone=phone, amount=amount)
        order.save()
        update = OrderUpdate(order_id=order.order_id, update_desc="The order has been placed")
        update.save()
        thank = True
        id = order.order_id
        return render(request, 'shopping/checkout.html', {'thank':thank, 'id': id})
    return render(request, 'shopping/checkout.html')



def cancel_order(request, order_id):
    try:
        order = Orders.objects.get(order_id=order_id)
        # Implement your cancellation logic here
        # For example, you might want to set the status of the order to "Cancelled"
        order.status = 'Cancelled'
        order.save()
        
        # Add an entry in OrderUpdate for the cancellation
        update = OrderUpdate(order_id=order_id, update_desc="Order has been cancelled.")
        update.save()
        
        return render(request, 'shopping/tracker.html')
        #return redirect('order_status', order_id=order_id)  # Redirect to order status page
    except Orders.DoesNotExist:
        return HttpResponse("Order not found.")

def return_order(request, order_id):
    try:
        order = Orders.objects.get(order_id=order_id)
        # Implement your return logic here
        # For example, you might want to set the status of the order to "Returned"
        order.status = 'Returned'
        order.save()
        
        # Add an entry in OrderUpdate for the return
        update = OrderUpdate(order_id=order_id, update_desc="Order has been returned.")
        update.save()
        
        return render(request, 'shopping/tracker.html')
        #return redirect('order_status', order_id=order_id)  # Redirect to order status page
    except Orders.DoesNotExist:
        return HttpResponse("Order not found.")
