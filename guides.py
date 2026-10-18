"""Guide landing pages for Nothing Down Board.

Each guide is a list of content blocks rendered by build.py.
Text may use [link text](/path) for internal links and {placeholders}
that build.py fills from today's data (see guide_context in build.py):
  {month}            e.g. October 2026
  {today}            e.g. Saturday, October 17, 2026
  {n_all}            total current offers
  {n_lease}, {n_lease_zero}, {n_finance}, {n_home}, {n_phone}, {n_solar}
  {lowest_lease}     e.g. "2026 Toyota Corolla LE at $296/mo"

Block types:
  ("p", text)
  ("h2", anchor_id, text)
  ("h3", text)
  ("ul", [text, ...]) / ("ol", [text, ...])
  ("table", caption, [headers], [[cells], ...])
  ("callout", title, text)
  ("offers", category, limit, zero_only)   live offers from today's data
  ("steps", [(title, text), ...])
"""

HUB = {
    "slug": "best-nothing-down-deals",
    "title": "The Best Nothing-Down Deals Right Now ({month}): 7 Types Ranked",
    "nav": "Best $0-down deals",
    "desc": "Which zero-down deals are actually worth it? We rank $0-due-at-signing leases, VA and USDA loans, free phones, 100% auto loans, doctor loans and $0-down solar, with today’s live offers.",
    "h1": "The best nothing-down deals, ranked",
    "eyebrow": "Guide · Updated {today}",
    "intro": "“No money down” shows up on car lots, mortgage ads and phone store windows, but the deals behave very differently once you sign. Here are the seven kinds of zero-down offers worth knowing, ranked by how much they save you up front and how few strings come attached.",
}

# Ranked list on the hub page. guide = slug of the matching guide page.
RANKED = [
    {
        "name": "VA home loans",
        "guide": "zero-down-home-loans",
        "category": "Home loan",
        "best_for": "Eligible service members, veterans and some surviving spouses",
        "why": "No down payment, no monthly mortgage insurance and no income cap. On a typical home that keeps tens of thousands of dollars in your pocket at closing.",
        "watch": "A one-time funding fee (2.3% of the loan for first use with nothing down) that can be rolled into the loan, and VA property standards.",
    },
    {
        "name": "$0-due-at-signing car leases",
        "guide": "zero-down-car-leases",
        "category": "Car lease",
        "best_for": "Drivers with strong credit who want a new car every few years",
        "why": "The most widely available zero-down deal. Brands publish them every month, and you drive away without writing a check.",
        "watch": "Fees and the first payment get rolled into a slightly higher monthly payment, and mileage caps apply.",
    },
    {
        "name": "USDA home loans",
        "guide": "zero-down-home-loans",
        "category": "Home loan",
        "best_for": "Moderate-income buyers in eligible rural and suburban areas",
        "why": "100% financing on a 30-year fixed loan, often with a lower ongoing fee than FHA mortgage insurance.",
        "watch": "Household income limits (generally 115% of the area median) and the home must be in an eligible area.",
    },
    {
        "name": "Free and $0-down phones",
        "guide": "free-phone-deals",
        "category": "Phone",
        "best_for": "People happy to stay with one carrier for three years",
        "why": "Carriers cover the full price of new phones through bill credits, so you can get a current flagship for nothing up front.",
        "watch": "Credits run 36 months, most deals need a new line, a trade-in or a premium plan, and leaving early ends the credits.",
    },
    {
        "name": "100% auto loans",
        "guide": "zero-down-car-loans",
        "category": "Car financing",
        "best_for": "Buyers who want to own the car and have good credit",
        "why": "Credit unions and some lenders finance the whole price, so you can buy without a down payment and keep the car as long as you like.",
        "watch": "Starting with no equity means you can owe more than the car is worth for the first year or two. Gap coverage helps.",
    },
    {
        "name": "Doctor and professional mortgages",
        "guide": "zero-down-home-loans",
        "category": "Home loan",
        "best_for": "Physicians, dentists and, at some banks, attorneys",
        "why": "Up to 100% financing with no private mortgage insurance, and lenders often count a signed job contract as income.",
        "watch": "Only offered in each bank’s states, and rates can run higher than a conventional loan with 20% down.",
    },
    {
        "name": "$0-down solar",
        "guide": "zero-down-solar",
        "category": "Home improvement",
        "best_for": "Homeowners with good sun exposure and high power bills",
        "why": "Panels go up with nothing paid at installation, and the monthly cost can be close to the bill it replaces.",
        "watch": "Leases and power purchase agreements often rise each year, and the federal homeowner solar credit ended after 2025.",
    },
]

HUB_BLOCKS = [
    ("callout", "The short answer",
     "If you qualify for a VA loan, it is the strongest zero-down deal there is. For everyone else with good credit, $0-due-at-signing leases are the easiest to find: there are {n_lease_zero} live today, starting with the {lowest_lease}. Free phones are a good deal only if you were going to stay with that carrier anyway."),
    ("ranked",),
    ("h2", "compare", "How the zero-down deals compare"),
    ("table", "Zero-down deal types side by side",
     ["Deal type", "Cash up front", "Who qualifies", "Biggest catch"],
     [
         ["VA loan", "$0 down; closing costs may apply", "Military service or eligible spouse", "Funding fee unless exempt"],
         ["$0-due-at-signing lease", "Nothing at all", "Top-tier credit, usually 700+", "Higher monthly payment, mileage limits"],
         ["USDA loan", "$0 down; closing costs may apply", "Income limit and eligible area", "Location and income rules"],
         ["Free phone", "Often tax only", "New line, trade-in or premium plan", "36 months of credits"],
         ["100% auto loan", "$0 down; taxes and fees may be financed", "Good credit, often membership", "Owing more than the car is worth"],
         ["Doctor mortgage", "0% to low down", "Medical, dental or legal degree", "Limited states, rate premium"],
         ["$0-down solar", "$0 at installation", "Homeowner with suitable roof", "Escalating payments on leases and PPAs"],
     ]),
    ("h2", "spot", "How to spot a real zero-down deal"),
    ("p", "The phrase “$0 down” only promises that you skip the down payment. It says nothing about the other money a deal can ask for at signing. Before you go in, check three things."),
    ("ol", [
        "**What is due at signing.** A lease can be $0 down and still want the first payment, a bank fee and registration on day one. Look for “$0 due at signing” if you want to pay nothing.",
        "**What the deal requires.** Most zero-down offers need top-tier credit, and many need something else: a trade-in, a new phone line, military service or a home in the right county.",
        "**Where the money went.** Nothing disappears. Skipped costs usually move into a higher payment, a funding fee or a longer term. Compare the total you will pay, not just the first check.",
    ]),
    ("p", "Every listing on [today’s board](/) shows what is due up front and what the offer requires, so you can rule deals in or out before you call anyone."),
    ("h2", "today", "Today’s zero-down offers by type"),
    ("p", "The board is checked every morning. Right now it has {n_all} live offers: {n_lease} car leases, {n_finance} car loans, {n_home} home loans, {n_phone} phone deals and {n_solar} solar options."),
]

HUB_FAQ = [
    ("What is the best zero-down deal?",
     "For eligible veterans and service members, a VA home loan is the strongest zero-down deal because it skips both the down payment and monthly mortgage insurance. For most other people with good credit, a $0-due-at-signing car lease is the easiest true zero-down offer to find."),
    ("Is no money down a good idea?",
     "It can be, if the monthly payment fits your budget and you understand where the skipped cost went. The risk is starting with no equity: on a car or home bought with nothing down, you can owe more than it is worth for a while."),
    ("What credit score do you need for zero-down deals?",
     "Advertised $0-due-at-signing leases usually assume top-tier credit, often around 700 or higher. VA and USDA loans set no official minimum, but most lenders look for scores in the 580 to 640 range or above."),
    ("Do zero-down deals cost more in the end?",
     "Often a little. Rolling fees into a lease raises the monthly payment, and VA loans add a funding fee. The trade is keeping your cash now, which can be worth it if that cash would otherwise sit in an emergency fund."),
]

GUIDES = [
    # ------------------------------------------------------------------ CAR LEASES
    {
        "slug": "zero-down-car-leases",
        "category": "Car lease",
        "nav": "$0 down car leases",
        "title": "$0 Down Car Leases ({month}): How They Work and Today’s Best Deals",
        "desc": "How $0 down and $0-due-at-signing car leases really work, what they cost, who qualifies, and the best zero-down lease deals live today.",
        "h1": "$0 down car leases: how they work and the best deals today",
        "eyebrow": "Car lease guide · Updated {today}",
        "intro": "A zero-down lease lets you drive a new car home without a big check at the dealership. It is one of the easiest nothing-down deals to find, but “$0 down” and “$0 due at signing” are not the same thing, and the difference shows up in your payment.",
        "blocks": [
            ("callout", "Today’s lowest $0-due-at-signing lease", "The {lowest_lease}, with nothing due when you sign. See all {n_lease} current [zero-down car leases](/car-leases/)."),
            ("offers", "Car lease", 6, True),
            ("h2", "difference", "$0 down vs. $0 due at signing"),
            ("p", "These two phrases get used as if they mean the same thing. They don’t."),
            ("table", "What each kind of lease asks for at signing",
             ["", "$0 down lease", "$0 due at signing lease"],
             [
                 ["Down payment (cap cost reduction)", "None", "None"],
                 ["First month’s payment", "Usually due at signing", "Rolled into the lease"],
                 ["Bank acquisition fee", "Often due at signing", "Rolled into the lease"],
                 ["Taxes, title and registration", "Often due at signing", "Rolled in where state law allows"],
                 ["Cash you bring", "Typically several hundred to a few thousand dollars", "Nothing"],
             ]),
            ("p", "A $0-due-at-signing lease spreads every upfront cost across the term, so the monthly payment is a bit higher. Toyota’s October Camry Hybrid lease, for example, is $0 down but still asks for the $359 first payment when you sign."),
            ("h2", "math", "What a $0 down lease really costs"),
            ("p", "Money you don’t pay at signing doesn’t vanish; it moves into the payment. As a rough guide, every $1,000 you skip up front adds about $28 a month to a 36-month lease, before interest. That is why a lease advertised at $239 a month with $2,999 down can become roughly $320 a month with nothing down."),
            ("p", "The good news: putting money down on a lease is risky anyway. If the car is totaled or stolen early, insurance and gap coverage pay off the lease, but your down payment is usually gone. Paying nothing up front keeps that cash safe."),
            ("h2", "qualify", "Who qualifies for a zero-down lease"),
            ("ul", [
                "**Credit:** advertised $0-down programs assume top-tier credit, often a score around 700 or higher. Lower scores can still lease, but usually with money down or a security deposit.",
                "**Region:** many manufacturer offers are regional, so the same car can have different terms in California and New York.",
                "**Timing:** most programs run for a month and end on a set date, often the first business days of the next month.",
            ]),
            ("h2", "best", "Which brands offer the best $0 down leases"),
            ("p", "Mainstream brands publish the most zero-down leases. This month the lowest payments come from compact cars and small SUVs at Toyota, Hyundai, Mazda, Kia and Nissan, while Volkswagen’s Sign Then Drive event covers the first payment as well. Browse by brand: [Toyota](/deals/toyota/), [Honda](/deals/honda/), [Hyundai](/deals/hyundai/), [Kia](/deals/kia/), [Mazda](/deals/mazda/), [Nissan](/deals/nissan/), [Subaru](/deals/subaru/) and [Chevrolet](/deals/chevrolet/)."),
            ("h2", "tips", "How to get a zero-down lease approved"),
            ("steps", [
                ("Check your credit first", "Pull your score before you shop so you know whether you fit the top tier the ad assumes."),
                ("Ask for the deal in writing", "Request a quote that lists the selling price, money factor, residual, acquisition fee and total due at signing."),
                ("Compare the total cost", "Multiply the payment by the term and add anything due at signing. Use that number to compare cars and dealers."),
                ("Pick your mileage honestly", "Overage charges often run 15 to 25 cents a mile. Paying for extra miles up front is usually cheaper."),
                ("Watch the add-ons", "Paint protection, tire packages and extended warranties can quietly erase a good zero-down deal."),
            ]),
        ],
        "faq": [
            ("Can you really lease a car with nothing down?",
             "Yes. Many brands and dealers offer $0-due-at-signing leases to buyers with strong credit. Every upfront cost, including the first payment and fees, is added to the monthly payment."),
            ("Is it smart to put $0 down on a lease?",
             "Often, yes. A lease down payment only lowers your monthly payment, and it can be lost if the car is totaled early. Many experts suggest putting as little down as possible on a lease."),
            ("What credit score do I need for a $0 down lease?",
             "Advertised zero-down lease programs usually assume top-tier credit, commonly around 700 or higher. Requirements vary by lender and brand."),
            ("Does $0 down mean $0 due at signing?",
             "No. $0 down means no down payment, but you may still owe the first payment, fees and taxes at signing. $0 due at signing means you pay nothing when you sign."),
        ],
        "related": ["zero-down-car-loans", "best-nothing-down-deals"],
    },
    # ------------------------------------------------------------------ CAR LOANS
    {
        "slug": "zero-down-car-loans",
        "category": "Car financing",
        "nav": "No money down car loans",
        "title": "How to Buy a Car With No Money Down ({month})",
        "desc": "Zero-down car loans explained: who offers 100% auto financing, what it costs, how to avoid being upside down, and today’s live no-money-down auto loan offers.",
        "h1": "How to buy a car with no money down",
        "eyebrow": "Car loan guide · Updated {today}",
        "intro": "Buying a car with no money down means financing the full price, and sometimes the taxes and fees too. It is possible with good credit, but it changes the math on what you owe and for how long.",
        "blocks": [
            ("offers", "Car financing", 4, False),
            ("h2", "how", "How a zero-down car loan works"),
            ("p", "With a zero-down auto loan, the lender covers 100% of the purchase price. Some lenders will also finance sales tax, registration and dealer fees, so you leave with no cash out of pocket. Credit unions are the most common source; Navy Federal, for example, advertises 100% financing to members."),
            ("p", "Dealer ads for 0% APR are a different thing. They lower the interest rate but usually still expect a down payment, so they are not on our list unless the lender says no money down."),
            ("h2", "risk", "The real risk: negative equity"),
            ("p", "A new car can lose a large share of its value in the first year. If you put nothing down, the loan balance can sit above the car’s value for a year or two. That matters if the car is totaled or you want to sell or trade it early."),
            ("ul", [
                "**Gap coverage** pays the difference between your insurance payout and the loan balance. It is often cheaper from your insurer or credit union than from the dealer.",
                "**Shorter terms** build equity faster. A 48- or 60-month loan with no money down is safer than an 84-month one.",
                "**Rolling in an old balance** is the move to avoid. Adding negative equity from a trade-in deepens the hole from day one.",
            ]),
            ("h2", "lease-or-loan", "Zero-down loan or zero-down lease?"),
            ("table", "Buying vs. leasing with nothing down",
             ["", "Zero-down loan", "$0-due-at-signing lease"],
             [
                 ["You own the car", "Yes, once paid off", "No; return or buy at lease end"],
                 ["Monthly payment", "Higher", "Lower for the same car"],
                 ["Mileage limits", "None", "Usually 10,000 to 12,000 miles a year"],
                 ["Equity risk", "Can be upside down early", "Covered by built-in gap on most leases"],
                 ["Best for", "Keeping a car 5+ years", "A new car every 2 to 3 years"],
             ]),
            ("p", "If a low payment matters most, compare against today’s [$0-due-at-signing leases](/guides/zero-down-car-leases/)."),
            ("h2", "approved", "How to get approved with no money down"),
            ("steps", [
                ("Get preapproved before the dealer", "A credit union or bank preapproval tells you your rate and how much you can finance, and gives you leverage."),
                ("Keep the price within your budget", "Lenders are more willing to finance 100% when the payment is a modest share of your income."),
                ("Check your debt-to-income ratio", "Paying down a credit card before you apply can improve both your score and your approval odds."),
                ("Bring proof of income", "Recent pay stubs and a steady job history make a zero-down approval easier."),
            ]),
        ],
        "faq": [
            ("Can I buy a car with no money down?",
             "Yes, if your credit is strong enough for a lender to finance the full price. Credit unions are a common source of 100% auto loans."),
            ("What credit score do you need to finance a car with no money down?",
             "There is no single cutoff, but zero-down approvals with good rates usually go to borrowers in the good-to-excellent range, roughly 670 and above."),
            ("Is 0% APR the same as no money down?",
             "No. 0% APR means no interest. Most 0% APR dealer offers still expect a down payment."),
        ],
        "related": ["zero-down-car-leases", "best-nothing-down-deals"],
    },
    # ------------------------------------------------------------------ HOME LOANS
    {
        "slug": "zero-down-home-loans",
        "category": "Home loan",
        "nav": "0% down home loans",
        "title": "Zero Down Home Loans ({month}): VA, USDA and Other 0% Down Mortgages",
        "desc": "Every way to buy a house with no down payment: VA loans, USDA loans, credit-union 100% financing and doctor loans, with fees, eligibility and today’s live programs.",
        "h1": "Zero down home loans: every way to buy with 0% down",
        "eyebrow": "Mortgage guide · Updated {today}",
        "intro": "A 20% down payment on a typical home is out of reach for many buyers. A handful of mortgage programs skip the down payment entirely. Here is how each one works, who qualifies and what it costs.",
        "blocks": [
            ("offers", "Home loan", 7, False),
            ("h2", "compare", "The zero-down mortgage options compared"),
            ("table", "0% down mortgage programs",
             ["Program", "Who qualifies", "Upfront fee", "Monthly mortgage insurance"],
             [
                 ["VA loan", "Eligible service members, veterans, some surviving spouses", "Funding fee, 2.3% for first use with $0 down (can be financed; some veterans exempt)", "None"],
                 ["USDA Guaranteed loan", "Income up to about 115% of area median, eligible rural or suburban address", "Upfront guarantee fee (can be financed)", "Annual fee, paid monthly"],
                 ["Navy Federal Homebuyers Choice", "Navy Federal members, primary residence", "1.75% funding fee, waivable for a higher rate or 3% down", "None"],
                 ["Navy Federal Military Choice", "Members with military service", "1% origination plus 1.75% funding fee", "None"],
                 ["Doctor or professional loans", "Physicians, dentists, sometimes attorneys", "Varies by bank", "None"],
             ]),
            ("h2", "va", "VA loans: the best zero-down mortgage if you qualify"),
            ("p", "VA loans are backed by the Department of Veterans Affairs. With full entitlement there is no down payment, no monthly mortgage insurance and no income limit. You will need a Certificate of Eligibility, which your lender can usually request for you."),
            ("p", "The main cost is the funding fee. For a first-time VA borrower putting nothing down it is 2.3% of the loan, and it can be added to the loan instead of paid in cash. Veterans who receive VA disability compensation are generally exempt."),
            ("h2", "usda", "USDA loans: zero down outside big cities"),
            ("p", "USDA Guaranteed loans offer 100% financing on a 30-year fixed mortgage for a primary home in an eligible area. Eligible areas include many small towns and suburbs, not just farmland, so it is worth checking an address on the USDA eligibility map."),
            ("p", "Household income generally can’t exceed 115% of the area median, and USDA counts everyone in the household, not just the borrowers. Limits are higher in expensive areas such as much of California."),
            ("h2", "other", "Other ways to buy with nothing down"),
            ("ul", [
                "**Credit-union 100% financing.** Navy Federal’s Homebuyers Choice loan needs no down payment and no PMI for members buying a primary home.",
                "**Doctor loans.** Banks such as TD Bank, First Bank and Northwest Bank offer up to 100% financing with no PMI for physicians and dentists in their service areas. See [today’s doctor loan listings](/home-loans/).",
                "**Down payment assistance.** State housing agencies and some banks offer grants or forgivable second loans that can cover a 3% to 3.5% down payment, which can effectively make an FHA or conventional loan zero down.",
            ]),
            ("h2", "closing", "Zero down isn’t zero cash"),
            ("p", "Even with no down payment, buyers usually pay closing costs: appraisal, title, lender fees and prepaid taxes and insurance, often 2% to 5% of the price. You can lower them by asking the seller for a credit, using lender credits for a slightly higher rate, or applying for a closing cost grant."),
            ("h2", "steps", "How to buy a home with no money down"),
            ("steps", [
                ("Check which program fits", "Military service points to VA; an eligible address and moderate income point to USDA; a medical degree points to a doctor loan."),
                ("Get preapproved", "A preapproval confirms the program, your budget and the cash you will need for closing costs."),
                ("Plan for closing costs", "Budget for them or negotiate a seller credit in your offer."),
                ("Keep a cushion", "With no down payment you start with little equity, so keep savings for repairs and surprises."),
            ]),
        ],
        "faq": [
            ("Can you buy a house with no money down?",
             "Yes. VA and USDA loans require no down payment for eligible buyers, and some credit unions and banks offer 100% financing programs. You will usually still pay closing costs."),
            ("What is the easiest zero-down home loan to get?",
             "For eligible service members and veterans, the VA loan is usually easiest because it has no income limit and no monthly mortgage insurance. For others, USDA loans are the main government option if the home is in an eligible area."),
            ("Do zero-down mortgages have higher rates?",
             "Not necessarily. VA loan rates are often competitive with or lower than conventional rates. Some lender-specific 100% programs trade a slightly higher rate for waived fees."),
            ("What credit score do I need for a zero-down mortgage?",
             "VA and USDA don’t set an official minimum, but most lenders look for roughly 580 to 640 or higher. Credit-union and doctor programs set their own requirements."),
        ],
        "related": ["best-nothing-down-deals", "zero-down-solar"],
    },
    # ------------------------------------------------------------------ PHONES
    {
        "slug": "free-phone-deals",
        "category": "Phone",
        "nav": "Free phone deals",
        "title": "Free Phone Deals ({month}): Are $0 Down Phones Really Free?",
        "desc": "How free and $0-down phone deals from AT&T, T-Mobile, Verizon and Metro work, what they require, the catch with 36-month bill credits, and today’s best offers.",
        "h1": "Free phone deals: are $0 down phones really free?",
        "eyebrow": "Phone deals guide · Updated {today}",
        "intro": "Every carrier advertises a free phone. Most of those deals are real, but they come with conditions that decide whether “free” saves you money or costs you more over three years.",
        "blocks": [
            ("offers", "Phone", 8, False),
            ("h2", "how", "How free phone deals work"),
            ("p", "When a carrier says a phone is free or “On Us,” you usually buy it on a 36-month installment plan and the carrier gives you a monthly bill credit that cancels the payment. Pay the bill for three years and the phone is paid off."),
            ("p", "Prepaid brands such as Metro by T-Mobile work differently: they cut the price at checkout or by rebate when you switch, with no installment plan."),
            ("h2", "catch", "The catches to check before you switch"),
            ("ul", [
                "**Leaving early.** If you cancel the line or pay the phone off early, the credits stop and the remaining balance comes due.",
                "**The plan you need.** Many of the best deals require a premium unlimited plan. A free phone on a $100 plan can cost more than a paid phone on a $50 plan.",
                "**New line or switch.** The biggest offers are usually for new lines or customers bringing their number from another carrier.",
                "**Trade-in condition.** Some deals accept any condition; others need a recent model in good shape.",
                "**Taxes and fees.** Sales tax on the full price and an activation fee are often due on day one.",
            ]),
            ("h2", "carriers", "Free phone deals by carrier"),
            ("table", "What each carrier’s free phone deals usually need",
             ["Carrier", "Typical requirement", "Existing customers?"],
             [
                 ["AT&T", "Trade-in on an eligible unlimited plan", "Often yes, with a trade-in"],
                 ["T-Mobile", "New line or switch on Experience More or Beyond", "Some deals"],
                 ["Verizon", "New line on an eligible myPlan, sometimes a trade-in", "Some deals"],
                 ["Metro by T-Mobile", "Switch and add a line on a qualifying prepaid plan", "Rarely"],
             ]),
            ("p", "See every live offer by carrier: [AT&T](/deals/at-t/), [T-Mobile](/deals/t-mobile/) and [Metro by T-Mobile](/deals/metro-by-t-mobile/)."),
            ("h2", "worth", "When a free phone is worth it"),
            ("p", "Add up three years of the required plan, then compare it with the plan you would choose anyway plus the phone’s price. If the totals are close and you like the carrier’s coverage where you live, the free phone is a good deal. If the deal forces you onto a much pricier plan, buying the phone outright and using a cheaper plan often wins."),
        ],
        "faq": [
            ("Are free phones from carriers really free?",
             "They are paid for with monthly bill credits, usually over 36 months. If you keep the line and qualifying plan for the full term, you pay nothing for the phone, though taxes and an activation fee may apply."),
            ("What happens if I cancel before the credits finish?",
             "The remaining credits stop and the rest of the phone’s balance becomes due."),
            ("Can existing customers get free phones?",
             "Sometimes. AT&T often extends trade-in deals to existing customers, while the largest T-Mobile and Verizon offers usually need a new line or a switch."),
        ],
        "related": ["best-nothing-down-deals"],
    },
    # ------------------------------------------------------------------ SOLAR
    {
        "slug": "zero-down-solar",
        "category": "Home improvement",
        "nav": "$0 down solar",
        "title": "$0 Down Solar ({month}): Loans vs. Leases vs. PPAs",
        "desc": "How $0-down solar works in 2026: solar loans, leases and power purchase agreements compared, the end of the federal homeowner credit, and how to choose.",
        "h1": "$0 down solar: loans vs. leases vs. PPAs",
        "eyebrow": "Solar guide · Updated {today}",
        "intro": "You can put solar panels on your roof without paying anything at installation. There are three ways to do it, and they lead to very different results over 20 years.",
        "blocks": [
            ("offers", "Home improvement", 4, False),
            ("h2", "options", "The three ways to go solar with nothing down"),
            ("table", "Zero-down solar options compared",
             ["", "$0-down solar loan", "Solar lease", "Power purchase agreement (PPA)"],
             [
                 ["Who owns the panels", "You", "The solar company", "The solar company"],
                 ["What you pay", "Fixed loan payment", "Fixed monthly rent", "A rate per kWh of solar power"],
                 ["Yearly increases", "No", "Often 1% to 3%", "Often 1% to 3%"],
                 ["Incentives and rebates", "Yours", "Kept by the owner", "Kept by the owner"],
                 ["Maintenance", "Your responsibility (warranties help)", "Usually included", "Usually included"],
                 ["Selling your home", "Pay off or transfer the loan", "Buyer must take over the lease", "Buyer must take over the PPA"],
             ]),
            ("h2", "2026", "What changed in 2026"),
            ("p", "The 30% federal tax credit for homeowners who buy solar (Section 25D) ended for systems paid for after December 31, 2025. Companies that own panels under a lease or PPA can still claim business credits, which is one reason leases and PPAs are being promoted heavily."),
            ("p", "In California, the main state rebate for home batteries (SGIP) has fully reserved its general budget, with only income-qualified programs left on a waitlist. Check your utility and state for current rebates before you sign."),
            ("h2", "choose", "How to choose"),
            ("ul", [
                "**Choose a loan** if you plan to stay in the home for years and want the savings to grow once it is paid off.",
                "**Choose a lease or PPA** if you want no maintenance worries and lower risk, and you are comfortable with the yearly increase.",
                "**Skip it** if your roof needs replacing soon or is heavily shaded. Fix the roof first.",
            ]),
            ("h2", "questions", "Questions to ask every installer"),
            ("steps", [
                ("What will I pay in year 1 and year 20?", "For leases and PPAs, ask for the escalator and the total over the contract."),
                ("How much will my power bill drop?", "Ask for an estimate based on your actual usage and your utility’s current export rate."),
                ("What happens when I sell?", "Ask how a transfer works and whether there are fees."),
                ("What is covered and for how long?", "Get the panel, inverter, workmanship and roof-penetration warranties in writing."),
            ]),
        ],
        "faq": [
            ("Is $0 down solar a good deal?",
             "It can be if the monthly cost is below your current power bill and stays below it over time. Compare the yearly escalator and the total cost over the contract, not just the first payment."),
            ("Can I still get the federal solar tax credit in 2026?",
             "Not as a homeowner buying solar. The residential credit ended for expenditures after December 31, 2025. Companies that own systems under leases and PPAs may still use business credits."),
            ("Does a solar lease make it harder to sell my house?",
             "It can. The buyer usually has to qualify for and take over the lease or PPA, which adds a step to the sale."),
        ],
        "related": ["zero-down-home-loans", "best-nothing-down-deals"],
    },
]
