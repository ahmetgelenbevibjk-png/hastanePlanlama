from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime
from .optimizer import ScheduleOptimizer

class RunOptimizationAPIView(APIView):

    def post(self,request):
        target_date=request.data.get('date')

        if not target_date:
            target_date=datetime.now().strftime("%Y-%m-%d")

        try:

            optimizer = ScheduleOptimizer(target_date_str=target_date)
            results=optimizer.optimize()
            saved_count=optimizer.save_schedule()

            return Response({
                'status':'success',
                'message':f'{saved_count} adet ameliyat başarıyla çizelgelendi ve kaydedildi.',
                'stats':results
            },status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                'status':'error',
                'message':f'Optimizasyon sırasında bir hata oluştu:{str(e)}'
            },status=status.HTTP_500_INTERNAL_SERVER_ERROR)






