from django.contrib.auth.decorators import login_required
from django.contrib import messages, auth
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from collections import  Counter
import sqlite3

from ..forms import UserUpdateForm, ProfileUpdateForm
from ..models import Profile
from ..decorators import user_is_employee


@login_required(login_url=reverse_lazy('jobs:login'))
def profile(request):
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        profile = Profile(user=request.user)
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST,
                                   request.FILES,
                                   instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, 'Your account has been updated!')
            return redirect('jobs:employee-profile')

    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'u_form': u_form,
        'p_form': p_form
    }

    return render(request, 'jobs/employee/profile.html', context)


def recommendJob(request):
    name=request.user.first_name
    connection = sqlite3.connect("db.sqlite3")
    with connection:
        cursor = connection.execute("SELECT id FROM jobsapp_user where first_name=?", (name,))
        dict = (cursor.fetchall())
        userid = dict[0][0]
    with connection:
        newcur=connection.execute("SELECT * FROM jobsapp_profile where user_id=?", (userid,))
        profile_detais=(newcur.fetchall())
        user_job_title=profile_detais[0][1]
        user_skill=[]
        if not profile_detais[0][7]=="":
            user_skill.append(profile_detais[0][7])
        if not profile_detais[0][8]=="":
            user_skill.append(profile_detais[0][8])
        if not profile_detais[0][9]=="":
            user_skill.append(profile_detais[0][9])
        if not profile_detais[0][10]=="":
            user_skill.append(profile_detais[0][10])
    with connection:
        applicnt=connection.execute("select * from  jobsapp_applicant")
        data_applicant=applicnt.fetchall()
    with connection:
        cur_employer=connection.execute("SELECT * from jobsapp_job")
        jobs = cur_employer.fetchall()
        cosine_sim = {}
        employer_id=0
        job_applied=0
        for job in jobs:
            job_details_title=job[1]

            if str(user_job_title).upper()==str(job_details_title).upper():
                employer_id = job[0]
                job_skills=[]
                if not job[7]=="":
                    job_skills.append(job[7])
                if not job[8]=="":
                    job_skills.append(job[8])
                if not job[9]=="":
                    job_skills.append(job[9])
                if not job[10]=="":
                    job_skills.append(job[10])
                employeeSkills_vals = Counter(user_skill)
                Em_Skills_vals = Counter(job_skills)

                # convert to word-vectors
                words = list(employeeSkills_vals.keys() | Em_Skills_vals.keys())
                a_vector = [employeeSkills_vals.get(word, 0) for word in words]
                b_vector = [Em_Skills_vals.get(word, 0) for word in words]

                len_a = sum(x * x for x in a_vector) ** 0.5
                len_b = sum(y * y for y in b_vector) ** 0.5
                dot = sum(x * y for x, y in zip(a_vector, b_vector))
                cosine_si = dot / (len_a * len_b)

                cosine_sim[str(employer_id)] = cosine_si
        #print(cosine_sim)

        #print(cosine_sim)
        try:
            job_id_to_use = (max(cosine_sim.keys(), key=(lambda k: cosine_sim[k])))
            employer_id = int(job_id_to_use)
            job_emp_cur = connection.execute("SELECT * from jobsapp_job where id=?", (job_id_to_use,))
            data_to_render = job_emp_cur.fetchall()[0]
            #print(employer_id, type(employer_id), userid, type(userid))
            for data_app in data_applicant:
                if data_app[2] == employer_id and data_app[3] == userid:
                   # print(data_app[2], data_app[3])
                    job_applied = True

            data_job_list=data_to_render+(job_applied,)
            data_job = {i: data_job_list[i] for i in range(0, len(data_job_list))}
            return render(request,"jobs/employee/recommend.html",{"recommended_job":data_job})
        except:
            return render(request,"jobs/employee/recommend.html")