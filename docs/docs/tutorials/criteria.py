import openhtf as htf

def get_criteria(criterion):
	criteria_dict = {
			"test_criterion":    htf.Measurement('test_criterion').in_range(18,22).doc('This measurement helps illustrate the criteria usage in spintop-openhtf')
			}
	return criteria_dict[criterion]
