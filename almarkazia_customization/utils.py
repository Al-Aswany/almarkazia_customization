from decimal import Decimal, ROUND_HALF_UP


ONES = {
	0: "صفر",
	1: "واحد",
	2: "اثنان",
	3: "ثلاثة",
	4: "أربعة",
	5: "خمسة",
	6: "ستة",
	7: "سبعة",
	8: "ثمانية",
	9: "تسعة",
	10: "عشرة",
	11: "أحد عشر",
	12: "اثنا عشر",
	13: "ثلاثة عشر",
	14: "أربعة عشر",
	15: "خمسة عشر",
	16: "ستة عشر",
	17: "سبعة عشر",
	18: "ثمانية عشر",
	19: "تسعة عشر",
}

TENS = {
	20: "عشرون",
	30: "ثلاثون",
	40: "أربعون",
	50: "خمسون",
	60: "ستون",
	70: "سبعون",
	80: "ثمانون",
	90: "تسعون",
}

HUNDREDS = {
	1: "مائة",
	2: "مائتان",
	3: "ثلاثمائة",
	4: "أربعمائة",
	5: "خمسمائة",
	6: "ستمائة",
	7: "سبعمائة",
	8: "ثمانمائة",
	9: "تسعمائة",
}

SCALES = (
	(1_000_000_000_000, "تريليون", "تريليونان", "تريليونات", "تريليونا"),
	(1_000_000_000, "مليار", "ملياران", "مليارات", "مليارا"),
	(1_000_000, "مليون", "مليونان", "ملايين", "مليونا"),
	(1_000, "ألف", "ألفان", "آلاف", "ألفا"),
)


def egyptian_money_in_words(amount, currency=None):
	amount = Decimal(str(amount or 0)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
	is_negative = amount < 0
	amount = abs(amount)

	pounds = int(amount)
	piastres = int((amount - Decimal(pounds)) * 100)

	parts = []
	if pounds:
		parts.append(format_currency_part(pounds, "جنيه مصري", "جنيهان مصريان", "جنيهات مصرية", "جنيها مصريا"))
	if piastres:
		parts.append(format_currency_part(piastres, "قرش", "قرشان", "قروش", "قرشا"))
	if not parts:
		parts.append("صفر جنيه مصري")

	prefix = "فقط سالب " if is_negative else "فقط "
	return prefix + " و".join(parts) + " لا غير"


def format_currency_part(number, singular, dual, plural, counted):
	if number == 1:
		return singular
	if number == 2:
		return dual
	unit = get_unit_name(number, plural, counted)
	return f"{number_to_arabic_words(number)} {unit}"


def get_unit_name(number, plural, counted):
	last_two_digits = number % 100
	if 3 <= last_two_digits <= 10:
		return plural
	return counted


def number_to_arabic_words(number):
	number = int(number or 0)
	if number == 0:
		return ONES[0]
	if number < 0:
		return "سالب " + number_to_arabic_words(abs(number))

	parts = []
	remainder = number
	for scale, singular, dual, plural, counted in SCALES:
		count = remainder // scale
		remainder %= scale
		if count:
			parts.append(format_scale_part(count, singular, dual, plural, counted))

	if remainder:
		parts.append(number_below_thousand_to_words(remainder))

	return " و".join(parts)


def format_scale_part(count, singular, dual, plural, counted):
	if count == 1:
		return singular
	if count == 2:
		return dual
	if 3 <= count <= 10:
		return f"{number_below_thousand_to_words(count)} {plural}"
	return f"{number_below_thousand_to_words(count)} {counted}"


def number_below_thousand_to_words(number):
	if number < 100:
		return number_below_hundred_to_words(number)

	hundreds = number // 100
	remainder = number % 100
	parts = [HUNDREDS[hundreds]]
	if remainder:
		parts.append(number_below_hundred_to_words(remainder))

	return " و".join(parts)


DIGIT_TRANSLATION = str.maketrans("0123456789,.", "٠١٢٣٤٥٦٧٨٩٬٫")


def format_egyptian_money(amount, currency=None):
	amount = Decimal(str(amount or 0)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
	return f"{amount:,.2f}".translate(DIGIT_TRANSLATION) + " جنيه مصري"


def number_below_hundred_to_words(number):
	if number < 20:
		return ONES[number]
	if number in TENS:
		return TENS[number]

	ones = number % 10
	tens = number - ones
	return f"{ONES[ones]} و{TENS[tens]}"
