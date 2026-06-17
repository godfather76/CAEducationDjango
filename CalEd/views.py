from django.db.models import Count
from django.views import generic
from django.contrib.gis.geos import fromstr
from django.contrib.gis.db.models.functions import Distance, Transform
from .models import *
from django.core.serializers import serialize
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
import json

def index(request):
    test = request.GET.get('test', 'SB - English Language Arts/Literacy')
    available_years = (
        AggByDistrictTA.objects
        .values_list('year', flat=True)
        .distinct()
        .order_by('year')
    )
    if not available_years:
        available_years = [2021, 2022, 2023]

    available_student_groups = (
        ELAMathTestScore.objects
        .values_list('student_group_name', flat=True)
        .distinct()
        .order_by('student_group_name')
    )

    elamath_tests = (
        ELAMathTestScore.objects
        .values_list('test_name', flat=True)
        .distinct()
        .order_by('test_name')
    )

    science_tests = (
        ScienceTestScore.objects
        .values_list('test_name', flat=True)
        .distinct()
        .order_by('test_name')
    )

    available_tests = elamath_tests.union(science_tests)

    elamath_grades = (
        ELAMathTestScore.objects
        .values_list('grade', flat=True)
        .distinct()
        .order_by('grade')
    )

    science_grades = (
        ScienceTestScore.objects
        .values_list('grade', flat=True)
        .distinct()
        .order_by('grade')
    )

    available_grades = elamath_grades

    available_scores = ['Mean Scale Score',
                        'Percentage Met and Above',
                        'Percentage Nearly Met']

    context = {
        'available_years': available_years,
        'available_student_groups': available_student_groups,
        'available_tests': available_tests,
        'available_grades': available_grades,
        'available_scores': available_scores,
    }
    return render(request, 'index.html', context)


def county_geo_json(request):
    staff_type = request.GET.get('staff_type', 'TA')
    year = request.GET.get('year', '2022')
    test = request.GET.get('test', 'SB - English Language Arts/Literacy')
    student_group = request.GET.get('student_group', 'All Students')
    grade = request.GET.get('grade', '11')

    # Get queryset
    counties = County.objects.all()

    model_mapping = {
        'T': AggByCountyT,
        'A': AggByCountyA,
        'S': AggByCountyS,
        'TA': AggByCountyTA,
        'TAS': AggByCountyTAS,
    }

    selected_agg_model = model_mapping.get(staff_type, AggByCountyTA)
    # Get information from the model and filter by year
    agg_records = selected_agg_model.objects.filter(year=year)
    # Return a dictionary with the data rows for lookup without requerying the db
    stats_lookup = {
        record.county: record for record in agg_records
    }

    score_model_mapping = {'SB - English Language Arts/Literacy': ELAMathTestScore,
                           'SB - Mathematics': ELAMathTestScore,
                           'CAST - California Science Test': ScienceTestScore}

    selected_score_model = score_model_mapping.get(test, 'SB - English Language Arts/Literacy')
    score_records = selected_score_model.objects.filter(
        test_name=test,
        district_code=0,
        school_code=0,
        student_group_name=student_group,
        grade=grade,
         year=year
    ).exclude(county_code=0)
    score_stats_lookup = {
        record.county_name: record for record in score_records
    }

    features = []
    for county in counties:
        if not county.geometry:
            continue
        stats = stats_lookup.get(county.county)
        score_stats = score_stats_lookup.get(county.county)
        stat_dict = {
            'county_name': stats.county if stats else 'N/A',
            'regular_pay_min': stats.regular_pay_min if stats else 'N/A',
            'regular_pay_max': stats.regular_pay_max if stats else 'N/A',
            'regular_pay_mean': stats.regular_pay_mean if stats else 'N/A',
            'regular_pay_sum': stats.regular_pay_sum if stats else 'N/A',
            'overtime_pay_min': stats.overtime_pay_min if stats else 'N/A',
            'overtime_pay_max': stats.overtime_pay_max if stats else 'N/A',
            'overtime_pay_mean': stats.overtime_pay_mean if stats else 'N/A',
            'overtime_pay_sum': stats.overtime_pay_sum if stats else 'N/A',
            'other_pay_min': stats.other_pay_min if stats else 'N/A',
            'other_pay_max': stats.other_pay_max if stats else 'N/A',
            'other_pay_mean': stats.other_pay_mean if stats else 'N/A',
            'other_pay_sum': stats.other_pay_sum if stats else 'N/A',
            'total_pay_min': stats.total_pay_min if stats else 'N/A',
            'total_pay_max': stats.total_pay_max if stats else 'N/A',
            'total_pay_mean': stats.total_pay_mean if stats else 'N/A',
            'total_pay_sum': stats.total_pay_sum if stats else 'N/A',
            'benefits_min': stats.benefits_min if stats else 'N/A',
            'benefits_max': stats.benefits_max if stats else 'N/A',
            'benefits_mean': stats.benefits_mean if stats else 'N/A',
            'benefits_sum': stats.benefits_sum if stats else 'N/A',
            'total_pay_and_benefits_min': stats.total_pay_and_benefits_min if stats else 'N/A',
            'total_pay_and_benefits_max': stats.total_pay_and_benefits_max if stats else 'N/A',
            'total_pay_and_benefits_mean': stats.total_pay_and_benefits_mean if stats else 'N/A',
            'total_pay_and_benefits_sum': stats.total_pay_and_benefits_sum if stats else 'N/A',
            'total_enrollment': score_stats.total_enrollment if score_stats else 'N/A',
            'total_tested': score_stats.total_tested if score_stats else 'N/A',
            'total_tested_with_scores': score_stats.total_tested_with_scores if score_stats else 'N/A',
            'mean_scale_score': score_stats.mean_scale_score if score_stats else 'N/A',
            'percentage_met_above': score_stats.percentage_met_above if score_stats else 'N/A',
            'percentage_nearly_met': score_stats.percentage_nearly_met if score_stats else 'N/A',
        }



        features.append({
            'type': 'Feature',
            'geometry': json.loads(county.geometry.geojson),
            'properties': {
                x: y for x, y in stat_dict.items()
            }
        })
    return JsonResponse({"type": "FeatureCollection", "features": features})

def district_geo_json(request):
    staff_type = request.GET.get('staff_type', 'TA')
    year = request.GET.get('year', '2022')
    test = request.GET.get('test', 'SB - English Language Arts/Literacy')
    student_group = request.GET.get('student_group', 'All Students')
    grade = request.GET.get('grade', '11')

    districts = SchoolDistrict.objects.all()
    model_mapping = {
        'T': AggByDistrictT,
        'A': AggByDistrictA,
        'S': AggByDistrictS,
        'TA': AggByDistrictTA,
        'TAS': AggByDistrictTAS,
    }
    # Select an agg model based on dropdown state. If there is an issue, default to district teachers and admins data.
    selected_agg_model = model_mapping.get(staff_type, AggByDistrictTA)
    # Make a dictionary with the data rows for lookup without requerying the db
    agg_records = selected_agg_model.objects.filter(year=year)
    # Return a dictionary with the data rows for lookup without requerying the db
    stats_lookup = {
        record.district: record for record in agg_records
    }

    score_model_mapping = {'SB - English Language Arts/Literacy': ELAMathTestScore,
                           'SB - Mathematics': ELAMathTestScore,
                           'CAST - California Science Test': ScienceTestScore}

    selected_score_model = score_model_mapping.get(test, 'SB - English Language Arts/Literacy')
    score_records = selected_score_model.objects.filter(
        test_name=test,
        school_code=0,
        student_group_name=student_group,
        grade=grade,
        year=year
    ).exclude(district_code=0)
    score_stats_lookup = {
        record.district_name: record for record in score_records
    }

    features = []
    for district in districts:
        # Skip records missing spatial data to avoid JSON serialization errors.
        if not district.geometry:
            continue
        # Get the data for this district
        stats = stats_lookup.get(district.district_name)
        score_stats = score_stats_lookup.get(district.district_name)
        stat_dict = {
            'county_name': stats.county if stats else 'N/A',
            'regular_pay_min': stats.regular_pay_min if stats else 'N/A',
            'regular_pay_max': stats.regular_pay_max if stats else 'N/A',
            'regular_pay_mean': stats.regular_pay_mean if stats else 'N/A',
            'regular_pay_sum': stats.regular_pay_sum if stats else 'N/A',
            'overtime_pay_min': stats.overtime_pay_min if stats else 'N/A',
            'overtime_pay_max': stats.overtime_pay_max if stats else 'N/A',
            'overtime_pay_mean': stats.overtime_pay_mean if stats else 'N/A',
            'overtime_pay_sum': stats.overtime_pay_sum if stats else 'N/A',
            'other_pay_min': stats.other_pay_min if stats else 'N/A',
            'other_pay_max': stats.other_pay_max if stats else 'N/A',
            'other_pay_mean': stats.other_pay_mean if stats else 'N/A',
            'other_pay_sum': stats.other_pay_sum if stats else 'N/A',
            'total_pay_min': stats.total_pay_min if stats else 'N/A',
            'total_pay_max': stats.total_pay_max if stats else 'N/A',
            'total_pay_mean': stats.total_pay_mean if stats else 'N/A',
            'total_pay_sum': stats.total_pay_sum if stats else 'N/A',
            'benefits_min': stats.benefits_min if stats else 'N/A',
            'benefits_max': stats.benefits_max if stats else 'N/A',
            'benefits_mean': stats.benefits_mean if stats else 'N/A',
            'benefits_sum': stats.benefits_sum if stats else 'N/A',
            'total_pay_and_benefits_min': stats.total_pay_and_benefits_min if stats else 'N/A',
            'total_pay_and_benefits_max': stats.total_pay_and_benefits_max if stats else 'N/A',
            'total_pay_and_benefits_mean': stats.total_pay_and_benefits_mean if stats else 'N/A',
            'total_pay_and_benefits_sum': stats.total_pay_and_benefits_sum if stats else 'N/A',
            'mean_scale_score': score_stats.mean_scale_score if score_stats else 'N/A',
            'percentage_met_above': score_stats.percentage_met_above if score_stats else 'N/A',
            'percentage_nearly_met': score_stats.percentage_nearly_met if score_stats else 'N/A',
        }

        features.append({
            'type': 'Feature',
            'geometry': json.loads(district.geometry.geojson),
            'properties': {
                x: y for x, y in stat_dict.items()
            }
        })

    return JsonResponse({"type": "FeatureCollection", "features": features})