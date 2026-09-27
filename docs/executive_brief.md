# Executive Brief — Who should get a promotion?

**Online retailer · customer value & promotion targeting · 27 September 2026**

*All promotion figures are scenario-based simulations under stated assumptions. The data contain no promotion experiment, so they are not causal uplift or ROI.*

## Recommendation

1. **Do not run a broad discount campaign at 5–20% off.** In every planning scenario, sending offers to 10% of active customers, whether chosen at random or by RFM score, *loses* simulated margin: about £5.7k to £23k (random) and £14k to £56k (RFM) over two monthly campaigns. The reason is that 58% of these customers buy again within 90 days anyway, so most of the discount is given away.
2. **Use the targeting rule as a gate, not a volume target.** A customer receives an offer only if their predicted repeat probability is below a break-even threshold p\* (about **0.10–0.15** under our assumptions) *and* their expected order value is high. Net-returners are excluded. At today's assumptions the rule targets **nobody**. That is the correct, margin-protecting answer, not a failure.
3. **Run one small randomised test before any campaign.** Offer a 5% discount to about 550 low-probability, high-value customers and hold out a matched control group for 90 days. This measures the real incremental effect, the one number our analysis cannot observe.

## When targeting becomes worthwhile

Targeting pays off only when the offer's incremental effect is large relative to its cost. With a **5% discount** and an assumed **+10 percentage-point** lift in repeat purchase, the rule selects about 275 customers per month (10% capacity; 551 over the two test months) for an expected **+£276** in total. Random and RFM campaigns still lose £3.7k and £13.4k. At 20% off, no realistic lift makes the campaign profitable. Across 2,160 combinations of discount, lift, margin, contact cost, capacity and lift pattern, the rule never did worse than random or RFM targeting. In 84–88% of combinations it also did better than simply targeting the least-likely buyers.

## Who is who (test period, Aug–Sep 2011, 5,534 customer-months)

| Segment | Share | 90-day repeat rate | Median basket | Suggested action |
|---|---|---|---|---|
| High-value active | 22% | 84% | £382 | No discount; buy anyway |
| Developing | 23% | 66% | £261 | Nurture (content, not price) |
| High-value at risk | 8% | 66% | £547 | First candidates for the test |
| Low-value active | 10% | 42% | £187 | Low-cost channel only |
| Dormant | 37% | 40% | £214 | Test only if value is high |

## How reliable is the prediction?

The repeat-purchase model (logistic regression on recency, frequency, value, tenure and seasonality) ranks customers better than the RFM score on unseen months: precision 95% vs 90% among the top 10%, PR-AUC 0.82 vs 0.79. It was validated on later months than it was trained on, and the final test months were used only once. Its probabilities run high in autumn (predicted 70% vs actual 58%), but shifting them by ±12 points does not change the recommendation.

## Key assumptions (all visible in the configuration)

- **Incremental lift of an offer:** +2 / +5 / +10 points in repeat probability (conservative / base / aggressive). *Unknown; this is what the test must measure.*
- **Gross margin 40%** (gift/home-goods e-commerce benchmark, lower for wholesale buyers). **Contact cost £0.10** per customer (email).
- **Value of one extra order = the customer's average basket**, capped at £1,951 so that a few wholesalers do not dominate.

## Risks and limitations

- Results depend on the assumed lift; treat every £ figure as a planning estimate, not a forecast.
- 23% of transactions have no customer ID and are excluded. About 92% of activity is UK. Data are from 2009–2011, from a single retailer.
- Cancellations and returns cannot be separated. Seasonality is strong (Q4 peak).
- Loyal customers receive fewer offers under this rule; monitor satisfaction.

**Next step:** approve the 550-customer randomised holdout test (5% offer), then re-run this pipeline with the measured lift.
