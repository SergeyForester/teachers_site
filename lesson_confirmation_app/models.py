from django.contrib.auth.models import User
from django.db import models

# Create your models here.

class TeacherBill(models.Model):
	teacher = models.ForeignKey(User, on_delete=models.CASCADE)
	created_at = models.DateTimeField(auto_now_add=True)
	pay_by = models.DateTimeField()
	total_amount = models.DecimalField(max_digits=9, decimal_places=2)
	is_payed = models.BooleanField(default=False)

	def __str__(self):
		return f"{self.teacher.first_name} -> {self.total_amount}"