/** Placeholder OWL component - not loaded until assets are enabled in manifest **/
/** Enable later and mount through a client action or patch as needed **/
import { Component, useState } from "@odoo/owl";

export class SentimentMiniWidget extends Component {
    setup() {
        this.state = useState({ label: "Sentiment Ready", score: 0.0 });
    }
}
SentimentMiniWidget.template = "customer_sentiment_analysis.SentimentMiniWidget";
