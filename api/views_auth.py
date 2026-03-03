from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken
from drf_spectacular.utils import extend_schema, OpenApiResponse
from .serializers_auth import UserRegistrationSerializer, UserLoginSerializer, UserSerializer


@extend_schema(
    summary="Register a new user",
    request=UserRegistrationSerializer,
    responses={
        201: OpenApiResponse(
            response=UserSerializer,
            description="User created successfully"
        ),
        400: OpenApiResponse(description="Validation errors")
    }
)
@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    """
    Register a new user and return user data with JWT tokens.
    """
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        P
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token
        
        # Return user data with tokens
        user_serializer = UserSerializer(user)
        return Response({
            'user': user_serializer.data,
            'tokens': {
                'access': str(access_token),
                'refresh': str(refresh),
            }
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    summary="Login user",
    request=UserLoginSerializer,
    responses={
        200: OpenApiResponse(
            description="Login successful"
        ),
        400: OpenApiResponse(description="Invalid credentials")
    }
)
@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """
    Login user and return JWT tokens.
    """
    serializer = UserLoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token
        
        # Return user data with tokens
        user_serializer = UserSerializer(user)
        return Response({
            'user': user_serializer.data,
            'tokens': {
                'access': str(access_token),
                'refresh': str(refresh),
            }
        }, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    summary="Logout user",
    responses={
        200: OpenApiResponse(description="Logout successful"),
        400: OpenApiResponse(description="Invalid refresh token")
    }
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """
    Logout user by blacklisting the refresh token.
    """
    try:
        refresh_token = request.data.get('refresh_token')
        if not refresh_token:
            return Response({
                'error': 'Refresh token is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        token = RefreshToken(refresh_token)
        token.blacklist()
        
        return Response({
            'message': 'Logout successful'
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response({
            'error': 'Invalid refresh token'
        }, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    summary="Get current user profile",
    responses={
        200: UserSerializer
    }
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile_view(request):
    """
    Get current authenticated user profile.
    """
    serializer = UserSerializer(request.user)
    return Response(serializer.data)


@extend_schema(
    summary="Update current user profile",
    request=UserSerializer,
    responses={
        200: UserSerializer,
        400: OpenApiResponse(description="Validation errors")
    }
)
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_profile_view(request):
    """
    Update current authenticated user profile.
    """
    serializer = UserSerializer(request.user, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)