from django.contrib import admin
from .models import (
    FileUpload, FileConversion, CSVData, ShapefileData, KMLData, 
    FileShare, FileProcessingLog, ContactFormSubmission, UploadedParcel
)

# Register your models here.

@admin.register(ContactFormSubmission)
class ContactFormSubmissionAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'subject', 'submitted_at', 'is_resolved', 'user']
    list_filter = ['subject', 'is_resolved', 'submitted_at']
    search_fields = ['name', 'email', 'message']
    readonly_fields = ['submitted_at']
    list_editable = ['is_resolved']
    
    fieldsets = (
        ('Contact Information', {
            'fields': ('name', 'email', 'user')
        }),
        ('Message Details', {
            'fields': ('subject', 'message', 'submitted_at')
        }),
        ('Admin Management', {
            'fields': ('is_resolved', 'admin_notes'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')

@admin.register(UploadedParcel)
class UploadedParcelAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'kitta_no', 'district', 'municipality', 'file_type', 'uploaded_at', 'user']
    list_filter = ['file_type', 'district', 'municipality', 'uploaded_at']
    search_fields = ['name', 'kitta_no', 'district', 'municipality', 'ward']
    readonly_fields = ['id', 'uploaded_at']
    date_hierarchy = 'uploaded_at'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'user', 'name', 'kitta_no', 'sn_no')
        }),
        ('Location', {
            'fields': ('district', 'municipality', 'ward', 'location')
        }),
        ('File Information', {
            'fields': ('file_type', 'original_file', 'uploaded_at')
        }),
        ('Geometry', {
            'fields': ('geometry', 'coordinates'),
            'classes': ('collapse',)
        }),
    )
