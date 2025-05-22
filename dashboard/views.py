import datetime as dt
from datetime import datetime
from django.shortcuts import render, redirect,get_object_or_404

from django.http import HttpResponse
from .models import Patient, Doctor, User, Blog_Post, Appointment
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .google_calender import create_google_calendar_event

def index(request):
    return render(request,'home.html')


def login(request):
    if request.method == 'GET':
        return render(request,'login_form.html',{'show_toast':False})
    elif request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        print(f"Username: {username}")
        print(f"Password: {password}")
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            auth_login(request, user)
            message = 'Sent'
            success = True
            return redirect('profile')             

        else:
            message = 'User not found'
            success = False
            return render(request,'login_form.html',{'message':message,'show_toast':True,'success':success})

       
    
@login_required
def profile_view(request):
    user = request.user

    if not request.user.is_authenticated:
        return redirect('login')

    try:
        profile = Patient.objects.get(user=user)
        profile_type = 'patient'
        blog_posts = Blog_Post.objects.filter(draft=False)
        doctors = Doctor.objects.all()  # Ensure this fetches all doctors
        appointments = Appointment.objects.filter(patient=profile)

        return render(request, 'Profile/patient_profile.html', {'profile': profile, 'blog_posts': blog_posts, 'doctors': doctors, 'appointments': appointments})
    except Patient.DoesNotExist:
        try:
            profile = Doctor.objects.get(user=user)
            profile_type = 'doctor'
            blog_posts = Blog_Post.objects.filter(author=profile, draft=False)
            draft_blog_posts = Blog_Post.objects.filter(author=profile, draft=True)
            appointments = Appointment.objects.filter(doctor=profile)

            return render(request, 'Profile/doctor_profile.html', {'profile': profile, 'blog_posts': blog_posts, 'draft_blog_posts': draft_blog_posts, 'appointments': appointments})
        except Doctor.DoesNotExist:
            profile = None
            profile_type = None

    return redirect('login')  # Ensure there is a fallback redirect

    

def logout_view(request):
    logout(request)
    return redirect('login')

        

       

def signup(request):
    if request.method == 'GET':
        return render(request,'signup_form.html',{'show_toast':False})
    elif request.method == 'POST':
        # Extract data from the form
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        profile_picture = request.FILES.get('profile_picture')
        patient_profile_picture = request.FILES.get('patient_profile_picture')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        speciality = request.POST.get('speciality')
        license = request.POST.get('license')
        confirm_password = request.POST.get('confirm_password')
        address_line1 = request.POST.get('address_line1')
        city = request.POST.get('city')
        state = request.POST.get('state')
        pincode = request.POST.get('pincode')
        role = request.POST.get('role')

        # Print the form data to terminal for debugging
        print(f"First Name: {first_name}")
        print(f"Last Name: {last_name}")
        print(f"Profile Picture: {profile_picture}")
        print(f"patient_profile_picture: {patient_profile_picture}")
        print(f"Username: {username}")
        print(f"Email: {email}")
        print(f"Password: {password}")
        print(f"Confirm Password: {confirm_password}")
        print(f"Address Line 1: {address_line1}")
        print(f"City: {city}")
        print(f"State: {state}")
        print(f"Pincode: {pincode}")
        print(f"role: {role}")

        # Optionally, validate data (e.g., check if passwords match)
        if role == 'doctor':
            try:
                # Create a new user instance
                new_user = User(
                    first_name=first_name,
                    last_name=last_name,
                    username=username,
                    email=email,
                    # password=password,
                )
                new_user.set_password(password)
                new_user.save()

                new_doctor = Doctor(
                    user = new_user,
                    # profile_picture=profile_picture,
                    specialty = speciality,
                    license_number = license,
                    line1=address_line1,
                    city=city,
                    state=state,
                    pincode=pincode,
                )
                if profile_picture:
                    new_doctor.profile_picture = profile_picture
                else:
                    new_doctor.profile_picture = 'profile_pictures/default.png'



                new_doctor.save()
                message = 'Successfully submitted'
                success = True
            except Exception as e:
                message = 'Something went wrong!'
                success = False
                print("Something went wrong",e)
        elif role == 'patient':
            try:
                # Create a new user instance
                new_user = User(
                    first_name=first_name,
                    last_name=last_name,
                    username=username,
                    email=email,
                    # password=password,
                )
                new_user.set_password(password)

                new_user.save()

                new_patient = Patient(
                    user = new_user,
                    profile_picture=patient_profile_picture,
                    line1=address_line1,
                    city=city,
                    state=state,
                    pincode=pincode,
                )
                if patient_profile_picture:
                    new_patient.profile_picture = patient_profile_picture
                else:
                    new_patient.profile_picture = 'profile_pictures/default.png'

                new_patient.save()
                message = 'Successfully submitted'
                success = True
            except Exception as e:
                message = 'Something went wrong!'
                success = False
                print("Something went wrong",e)
        return render(request,'signup_form.html',{'message':message, 'show_toast': True,'success':success})
    

@login_required
def post_blog(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        category = request.POST.get('category')
        image = request.FILES.get('image')
        draft = request.POST.get('draft') 

        if draft:  
            is_draft = True
        else:
            is_draft = False
        lines = content.split('\n')
        summary = '\n'.join(lines[:2]) + "....."

        print(title, content, category, image)
        doctor = request.user
        profile = Doctor.objects.get(user=doctor)
        blog_post = Blog_Post(
            title=title,
            content=content,
            summary = summary, 
            category=category,
            image=image,
            author=profile,
            draft = is_draft

        )
        blog_post.save()
        success_message = "Your blog post has been successfully saved!"
    
    return redirect('/dash/profile/')

@login_required
def delete_post(request, post_id):
    print("inside delete")
    post = get_object_or_404(Blog_Post, id=post_id)
    
    if request.user != post.author.user:
        print("ERROR")
    if post:
        post.delete()
    return redirect('/dash/profile')

@login_required
def update_post(request):
    if request.method == 'POST':
        post_id = request.POST.get('post_id')
        print("posstid", post_id)
        title = request.POST.get('title')
        print("posstitlte", title)

        content = request.POST.get('content')
        category = request.POST.get('category')
        draft = request.POST.get('draft')

        post = get_object_or_404(Blog_Post, id=post_id)

        post.title = title
        post.content = content
        post.category = category
        post.draft = True if draft == 'on' else False 
        if 'image' in request.FILES:
            post.image = request.FILES['image']
        post.save()
        return redirect('/dash/profile')
    


def convert_to_iso_format_with_end_time(date_str, time_str):
    try:
        # Parse date and time strings
        date_obj = datetime.strptime(date_str, "%m/%d/%Y")
        time_obj = datetime.strptime(time_str, "%H:%M").time()

        # Combine date and time into a datetime object
        combined_datetime = datetime.combine(date_obj.date(), time_obj)

        # Add 45 minutes to the combined datetime
        end_datetime = combined_datetime + dt.timedelta(minutes=45)

        # Format end datetime into ISO 8601 format
        iso_start = combined_datetime.isoformat()
        iso_end = end_datetime.isoformat()

        return iso_start, iso_end
    except ValueError as e:
        print(f"Error parsing date or time: {e}")
        return None, None
    
@login_required
def book_appointment(request):
    if request.method == 'POST':
            patient_id = request.POST.get('patient_id')
            doctor_id = request.POST.get('doctor_id')
            appointment_date = request.POST.get('appointment_date')
            appointment_time = request.POST.get('appointment_time')
            required_speciality = request.POST.get('required_speciality')
            print("APPP",appointment_time)
            p_user = User.objects.get(id=patient_id)
            d_user = User.objects.get(id=doctor_id)

            doctor = Doctor.objects.get(user=d_user)
            patient = Patient.objects.get(user=p_user)
            original_date = datetime.strptime(appointment_date, "%m/%d/%Y")
    
            formatted_date = original_date.strftime("%Y-%m-%d")
            text_date = str(appointment_date)
            text_time = str(appointment_time)
            print("TIEM SDJNSKDJFNK",str(appointment_date), str(appointment_time))
            iso_start_datetime, iso_end_datetime = convert_to_iso_format_with_end_time(str(appointment_date), str(appointment_time))

            appointment_start_time = datetime.strptime(appointment_time, '%H:%M').time()

            # Calculate end time by adding 45 minutes to start time
            end_time = (datetime.combine(datetime.today(), appointment_start_time) + dt.timedelta(minutes=45)).time()
            print("Calendar event created for the Doctor",end_time)

            appointment = Appointment(
                doctor =doctor,
                patient=patient,
                required_speciality = required_speciality,
                date = formatted_date,
                time = appointment_time,
                end_time = end_time
            )
            print("ISOSSOOSS", iso_start_datetime, iso_end_datetime)
            appointment_data = {
                'doctor' : doctor,
                'patient' : patient,
                'startdatetime' : iso_start_datetime,
                'enddatetime' : iso_end_datetime
            }
            
            # Create Google Calendar event
            event = create_google_calendar_event(appointment_data)
            appointment.google_event_id = event['id']
            appointment.save()
            print("Calendar event created for the Doctor")
    return redirect('profile')

# @login_required
# def update_appointment(request):
#     if request.method == 'POST':
#         appointment_id = request.POST.get('appointment_id')
#         status = request.POST.get('status')  # 'confirmed' or 'cancelled'

#         appointment = get_object_or_404(Appointment, id=appointment_id)

#         # Update appointment status
#         if status == 'confirmed':
#             appointment.status = 'Confirmed'
#             # Optionally, create Google Calendar event if confirmed
#             iso_start_datetime, iso_end_datetime = convert_to_iso_format_with_end_time(str(appointment.appointment_date),str(appointment.appointment_time))
#             appointment_data = {
#                 'doctor' : appointment.doctor,
#                 'patient' : appointment.patient,
#                 'startdatetime' : iso_start_datetime,
#                 'enddatetime' : iso_end_datetime
#             }
#             event = create_google_calendar_event(appointment_data)
#             appointment.google_event_id = event['id']  # Assuming you save event ID in appointment model
#             appointment.save()
#             print("Appointment confirmed and Google Calendar event created.")
#         elif status == 'cancelled':
#             appointment.status = 'cancelled'
#             appointment.save()
#             print("Appointment cancelled.")

#     return redirect('profile')