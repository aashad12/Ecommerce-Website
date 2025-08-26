from django.db import models
from category.models import Category
from django.urls import reverse
from django.conf import settings
from django.contrib.auth.models import User

# Create your models here.
class Product(models.Model):
    owner = models.ForeignKey(  # who submitted it
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="products",
        null=True, 
        blank=True,  # allow null for old data / admin-created
    )
    product_name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField(max_length=1000, blank=True)
    price = models.IntegerField()
    images = models.ImageField(upload_to='photos/products/')
    stock = models.IntegerField()
    status = models.BooleanField(default=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    
    # single approval switch
    is_approved = models.BooleanField(default=False)
    
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    
    def get_url(self):
        # self.category.slug is slug of category, and self.slug is slug of product
        return reverse('product_detail', args=[self.category.slug, self.slug])

    
    def __str__(self):
        return self.product_name
    
variation_category_choices = {
    ('color', 'Color'),
    ('size', 'Size'),
}

# To modify the query set
class VariationManager(models.Manager):
    def colors(self):
        return super(VariationManager, self).filter(variation_category = 'color', is_active=True)
    
    def sizes(self):
        return super(VariationManager, self).filter(variation_category='size', is_active=True)
    
    
class Variation(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variation_category = models.CharField(max_length=100, choices=variation_category_choices)
    variation_value = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now=True)
    
    # Telling the model about the variation manager
    objects = VariationManager()
    
    def __str__(self):
        return self.variation_value
    
    
class StockRequest(models.Model):
    product = models.ForeignKey('store.Product', on_delete=models.CASCADE)  
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} requested {self.product}"
    
    
class Message(models.Model):
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='sent_messages', on_delete=models.CASCADE
    )
    product = models.ForeignKey('store.Product', on_delete=models.CASCADE, null=True, blank=True)
    subject = models.CharField(max_length=255, blank=True)
    body = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        sender_name = getattr(self.sender, 'username', str(self.sender))
        if self.product:
            return f"Message from {sender_name} about {self.product}"
        return f"Message from {sender_name}"