# Product Requirements Document (PRD)
## AI Multifamily Deep Research & Decision Engine

**Version**: 1.0 (MVP)
**Status**: Ready for Build
**Last Updated**: January 18, 2026

---

## 1. Executive Summary

### 1.1 Vision
A web-based "Deep Research & Decision Engine" for multifamily real estate investors that automates the top-of-funnel due diligence phase by performing live 1-3-5 mile demographic analysis and evaluating deals against strict, proprietary "Secret Sauce" criteria.

### 1.2 Core Value Proposition
**Reduces weeks of manual research to minutes** while enforcing institutional discipline to prevent "deal fever."

### 1.3 Target Users
- **Primary**: Acquisition Managers at multifamily investment firms
- **Secondary**: Investment Committee Members
- **Use Case**: Initial screening of potential property acquisitions

---

## 2. User Experience (UX)

### 2.1 User Persona

**Name**: Sarah Martinez
**Role**: Acquisition Manager, Apex Multifamily Capital
**Pain Points**:
- Spends 8-12 hours researching each potential deal
- Risk of "deal fever" causing emotional decision-making
- Difficulty applying consistent criteria across opportunities
- Manual demographic data gathering is tedious and error-prone

**Goals**:
- Screen 10+ deals per week instead of 2-3
- Apply institutional-grade criteria consistently
- Present data-backed recommendations to Investment Committee
- Avoid wasting time on fundamentally flawed opportunities

### 2.2 User Journey

#### Phase 1: Input
1. User navigates to web application
2. Enters **Property Address** (e.g., "123 Main St, Austin, TX 78701")
3. Enters **Deal Name** (e.g., "Sunset Apartments")
4. **Context Upload** (Optional but recommended):
   - Uploads Tax Abatement Agreements
   - Uploads Rent Rolls with actual tenant data
   - Uploads Appraisal Reports
   - Uploads Economic Development Incentives

#### Phase 2: Processing (Automated)
1. System identifies **Macro Context** (MSA level: Austin Metro)
2. System identifies **Micro Context** (Sub-market: Downtown Austin)
3. AI Agent performs live research:
   - 1-mile radius: Crime, renter density, competitive properties
   - 3-mile radius: Schools, amenities, development activity
   - 5-mile radius: Transport, path of growth
4. Logic Engine evaluates data against **30-Point Criteria**
5. PDF generation service creates deliverables

#### Phase 3: Output
1. User receives notification (email or in-app)
2. Downloads **Decision Heat Map** (Grid PDF)
   - Visual traffic light grid (Green/Yellow/Red)
   - All 30 criteria at a glance
   - Summary recommendation
3. Downloads **Investment Brief** (Narrative PDF)
   - Detailed reasoning for each criterion
   - Source citations
   - Final recommendation with justification

### 2.3 Success Metrics
- **Time Savings**: Reduce research time from 8 hours to <15 minutes
- **Accuracy**: 95%+ agreement with Investment Committee decisions
- **Throughput**: Enable 5x more deal screening per week
- **False Negatives**: <5% (don't reject good deals)
- **False Positives**: <10% (don't approve bad deals)

---

## 3. Functional Requirements

### 3.1 The "Context Container" Logic

The system must hierarchically separate data analysis to apply the correct passing criteria:

#### 3.1.1 Macro Container (MSA)
**Purpose**: Evaluates region-wide metrics that apply to all deals in that market.

**Criteria** (16 points):
- Population Size, Growth, Employment, Income
- Migration patterns, Job Diversity, Environmental Risk
- Unemployment, Vacancy Rates, Cap Rates
- Permits, Absorption, Legal Environment
- Affordability, Proximity to Tier 1 MSAs

**Logic**: These signals are market-level and don't change based on specific property location within the MSA.

#### 3.1.2 Micro Container (Sub-Market)
**Purpose**: Evaluates location-specific metrics within 1-3-5 mile radii.

**Criteria** (14 points):
- Crime, Schools, Amenities, Transport Access
- Path of Growth, Zoning, Renter Density
- Competitive Landscape, Taxes/Fees
- Appreciation, Government Volatility

**Logic**: These signals vary dramatically within an MSA based on specific address.

#### 3.1.3 Dynamic Criteria Application
The AI must detect location type and apply context-aware thresholds:

**Urban Core** (Downtown, Central Business District):
- High renter density (>70%) = GREEN (expected for urban)
- Proximity to transport (<0.5 mi) = YELLOW (noise tolerated)
- Lower school ratings = YELLOW (families less common)

**Suburban** (Periphery, Exurbs):
- Renter density >70% = YELLOW (may signal economic distress)
- Proximity to transport (<0.5 mi) = RED (quality of life concern)
- School ratings critical = RED if below threshold

### 3.2 Contextual Data Override (Critical Feature)

#### 3.2.1 The Problem
Generic market data can be misleading for specific properties:
- Market shows 2.5% property tax rate
- But this property has a 25-year tax abatement (0%)
- Without override, AI incorrectly flags taxes as RED

#### 3.2.2 The Solution
**Hierarchy of Truth**:
1. **Tier 1**: User-uploaded property-specific documents
2. **Tier 2**: Live research data (Perplexity, Census)
3. **Tier 3**: General market data

#### 3.2.3 Implementation
When user uploads a document:
1. AI extracts text and identifies document type
2. Searches for facts relevant to each criterion
3. If found, marks `override_applied: true`
4. Cites specific document and section in source field
5. Highlights override in PDF output with 📄 icon

#### 3.2.4 Common Override Scenarios
| Criterion | Market Data | Override Document | Result |
|-----------|-------------|-------------------|---------|
| Taxes/Fees | 2.3% county rate | Tax Abatement: 0% for 10 years | GREEN |
| Vacancy Rate | 8.2% MSA vacancy | Rent Roll: 98% occupancy | YELLOW* |
| Crime Rate | High neighborhood crime | Private security report | Context noted |
| Appreciation | 2% MSA growth | Appraisal: 5% property growth | GREEN |

*Still YELLOW because high MSA vacancy signals market risk despite property performance

### 3.3 Deep Research Agent (Data Points)

The AI must automatically harvest the following data:

#### 3.3.1 Demographics (MSA + Sub-Market)
- Total population (current + 5-year trend)
- Population density (per sq mi)
- Age cohorts:
  - % age 18-30 (peak renter demographic)
  - % age 55+ (downsizing empty nesters)
- Peak earning cohort (30-55) income vs. median
- Education: % with Bachelor's degree or higher
- Housing tenure: % renters vs. owners

#### 3.3.2 Economics (MSA)
- Total employment + 3-year growth rate
- Industry diversity (top 5 employers by %)
- Unemployment rate vs. national average
- Median household income + growth rate
- Income distribution (Gini coefficient)

#### 3.3.3 Real Estate Market (MSA)
- Apartment vacancy rate (current quarter)
- Average cap rate (Class B multifamily)
- Multifamily permits (trailing 12 months)
- Absorption rate (months to absorb pipeline)
- Rent growth (3-year CAGR)
- For-sale home inventory (months of supply)

#### 3.3.4 Validation Data (Sub-Market)
- **Crime**: Violent + Property crime per 1,000 residents
  - Compare to MSA average (% above/below)
  - Source: FBI UCR or NeighborhoodScout
- **Schools**: GreatSchools ratings for schools within 3 miles
  - Average rating
  - Distance to nearest rated school (>5/10)
- **Amenities**: "Goldilocks" principle (1-2 mi ideal)
  - Grocery stores
  - Big box retail
  - Restaurants/entertainment
  - Parks and recreation
- **Transport**: Path of growth indicators
  - Distance to highway on-ramp
  - Distance to public transit hub
  - New transit projects (light rail, BRT)
  - Interstate corridors

### 3.4 The 30-Point Logic Engine

#### 3.4.1 Constraint
The AI **MUST evaluate ALL 30 criteria**. It cannot:
- Summarize (e.g., "Most criteria pass")
- Skip low-importance items
- Combine related criteria

**Why**: Investment decisions require comprehensive analysis. A single overlooked red flag can kill a deal.

#### 3.4.2 Grading System
Every criterion must receive:

**Status** (Traffic Light):
- 🟢 **GREEN**: Meets or exceeds threshold, no concerns
- 🟡 **YELLOW**: Close to threshold, marginal, requires human review
- 🔴 **RED**: Fails threshold, disqualifies deal unless exceptional circumstances

**Citation** (Source):
- Must include: Document/Database name + Year + Page/Section
- Examples:
  - "US Census ACS 2024, Table S2501"
  - "CoStar Market Report Q4 2024, pg 12"
  - "User-uploaded: Tax_Abatement.pdf, Section 4.2"

#### 3.4.3 Example Criterion Evaluation

```json
{
  "id": "msa_1",
  "metric": "Population Size",
  "threshold": ">400,000",
  "value": "2,200,000",
  "status": "GREEN",
  "reasoning": "MSA population of 2.2M exceeds 400k threshold by 5.5x, providing deep tenant pool and institutional investor liquidity. Large population reduces concentration risk and supports long-term demand.",
  "source": "US Census Bureau 2024 Population Estimates, Table PEPANNRSIP",
  "override_applied": false
}
```

---

## 4. Non-Functional Requirements

### 4.1 Performance
- Analysis completion: <3 minutes per property
- PDF generation: <30 seconds
- System uptime: 99.5%

### 4.2 Scalability
- Support 100+ analyses per day (MVP)
- Scale to 1,000+ per day (future)

### 4.3 Accuracy
- Data freshness: <6 months for demographic data
- Citation accuracy: 100% (every source must be real)

### 4.4 Security
- User documents encrypted at rest and in transit
- GDPR/CCPA compliant data handling
- No data retention beyond 30 days (unless user account)

### 4.5 Usability
- No training required for basic use
- Mobile-responsive interface
- Accessible (WCAG 2.1 Level AA)

---

## 5. Out of Scope (MVP)

The following features are **NOT** included in v1.0:

- ❌ User accounts / authentication
- ❌ Saved analyses / history
- ❌ Comparative analysis (multiple properties side-by-side)
- ❌ Custom criteria modification by user
- ❌ Integration with MLS or property databases
- ❌ Automated property monitoring/alerts
- ❌ Financial underwriting (NOI, IRR calculations)

These may be added in future versions based on user feedback.

---

## 6. Success Criteria

### 6.1 MVP Launch Criteria
- ✅ All 30 criteria evaluated correctly
- ✅ Context override logic functional
- ✅ Gauntlet test suite passes (7/7 tests)
- ✅ PDF outputs professional quality
- ✅ <3 minute average analysis time

### 6.2 User Acceptance Testing
- 10 pilot users complete 5 analyses each
- 80%+ report time savings vs. manual research
- 90%+ agree with final recommendations
- <5 critical bugs reported

---

## 7. Appendix

### 7.1 The "Secret Sauce" Philosophy

The 30-point criteria are based on institutional multifamily investment principles:

**Core Tenets**:
1. **Demographics Drive Demand**: Young professionals + downsizing boomers = renter pool
2. **Jobs Drive Incomes**: Employment growth → rent affordability → occupancy
3. **Supply Must Be Constrained**: Oversupply kills rent growth
4. **Location Beats Asset**: Best property in worst location loses to mediocre property in best location
5. **Goldilocks Principle**: Extremes are bad (too close/far, too hot/cold, etc.)

### 7.2 References
- Urban Land Institute: *Emerging Trends in Real Estate*
- NMHC: *Apartment Market Fundamentals*
- Green Street: *Multifamily Investment Criteria*
- Internal investment committee historical data

---

**Document Control**
Author: Product Team
Reviewed By: Investment Committee
Approved By: CTO
Next Review: Q2 2026
