import os
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from rest_framework import status, viewsets
from django.http import JsonResponse
from django.conf import settings
import joblib
import pandas as pd
from django.contrib.auth.models import User
from geopy.geocoders import Nominatim
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Location, Rating
from .serializers import LocationSerializer, RatingSerializer, UserSerializer


@api_view(['POST'])
def SafeUnsafe(request):
    try:
        print(request.data)
        ClassifierFile = 'ClassifierModel.pkl'
        RegressorFile = 'RegressorModel.pkl'
        ClassifierFile_path = os.path.join(settings.MODEL_ROOT, ClassifierFile)
        RegressorFile_path = os.path.join(settings.MODEL_ROOT, RegressorFile)

        with open(ClassifierFile_path, 'rb') as file:
            Classifier_Model = joblib.load(file)
        with open(RegressorFile_path, 'rb') as file:
            Regressor_Model = joblib.load(file)

        print(request.data)
        details = request.data

        locator = Nominatim(user_agent="myGeocoder", format_string="%s, Mumbai, India")
        location = locator.geocode(details["Location"])

        lat = [location.latitude]
        log = [location.longitude]
        latlong = pd.DataFrame({'latitude': lat, 'longitude': log})

        DT = details["DateTime"]
        latlong['Date-Time'] = DT
        test_data = latlong
        cols = test_data.columns.tolist()
        cols = cols[-1:] + cols[:-1]
        test_data = test_data[cols]

        test_data['Date-Time'] = pd.to_datetime(test_data['Date-Time'].astype(str), errors='coerce')
        test_data['Date-Time'] = pd.to_datetime(test_data['Date-Time'], format='%d/%m/%Y %H:%M:%S')

        TestColumn = test_data.iloc[:, 0]

        DT = pd.DataFrame({
            "year": TestColumn.dt.year,
            "month": TestColumn.dt.month,
            "day": TestColumn.dt.day,
            "hour": TestColumn.dt.hour,
            "minute": TestColumn.dt.minute,
            "weekday": TestColumn.dt.weekday
        })

        test_data = test_data.drop('Date-Time', axis=1)
        final = pd.concat([DT, test_data], axis=1)
        X_test = final.iloc[:, [1, 2, 3, 4, 5, 6, 7]].values

        CrimeType_Test = Classifier_Model.predict(X_test)
        SafetyIndex_Test = Regressor_Model.predict(X_test)

        print(CrimeType_Test)
        print(SafetyIndex_Test)
        if CrimeType_Test[0][0] == 1:
            Crime = 'Area is Prone to Robbery'
            Type = "Robbery"
            SafetyIndex = str(round(SafetyIndex_Test[0], 3))
        elif CrimeType_Test[0][1] == 1:
            Crime = 'Area is Prone to Theft'
            Type = "Theft"
            SafetyIndex = str(round(SafetyIndex_Test[0], 3))
        elif CrimeType_Test[0][2] == 1:
            Crime = 'Area is Prone to Murder'
            Type = "Murder"
            SafetyIndex = str(round(SafetyIndex_Test[0], 3))
        else:
            Crime = 'Area is safe'
            Type = "Safe"
            SafetyIndex = "5"
        result = {
            "Status": Crime,
            "SafetyIndex": SafetyIndex,
            "Crime": Type,
        }
        print(result)
        return JsonResponse(result)
    except ValueError as e:
        return Response(e.args[0], status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)


class LocationViewSet(viewsets.ModelViewSet):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated,)

    @action(detail=True, methods=['POST'])
    def rate_location(self, request, pk=None):
        if 'stars' in request.data:

            location = Location.objects.get(id=pk)
            stars = request.data['stars']
            user = request.user

            try:
                rating = Rating.objects.get(user=user.id, location=location.id)
                rating.stars = stars
                rating.save()
                serializer = RatingSerializer(rating, many=False)
                response = {'message': 'Rating updated', 'result': serializer.data}
                return Response(response, status=status.HTTP_200_OK)
            except:
                rating = Rating.objects.create(user=user, location=location, stars=stars)
                serializer = RatingSerializer(rating, many=False)
                response = {'message': 'Rating created', 'result': serializer.data}
                return Response(response, status=status.HTTP_200_OK)

        else:
            response = {'message': 'You need to provide stars'}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)


class RatingViewSet(viewsets.ModelViewSet):
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated,)

    def update(self, request, *args, **kwargs):
        response = {'message': 'You cant update rating like that'}
        return Response(response, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request, *args, **kwargs):
        response = {'message': 'You cant create rating like that'}
        return Response(response, status=status.HTTP_400_BAD_REQUEST)

