from django.contrib import admin
from .models import Persona, DomicilioPersona, EmailPersona, TelefonoPersona

class DomicilioInline(admin.TabularInline):
    model = DomicilioPersona
    extra = 1
    fields = ['calle', 'numero', 'piso', 'localidad', 'codigo_postal', 'principal']

class EmailInline(admin.TabularInline):
    model = EmailPersona
    extra = 1
    fields = ['email', 'principal', 'validado']

class TelefonoInline(admin.TabularInline):
    model = TelefonoPersona
    extra = 1
    fields = ['caracteristica', 'numero', 'tipo', 'principal']

@admin.register(Persona)
class PersonaAdmin(admin.ModelAdmin):
    list_display = ['personaid', 'apellido', 'nombre', 'documento']
    search_fields = ['apellido', 'nombre', 'documento']
    inlines = [DomicilioInline, EmailInline, TelefonoInline]