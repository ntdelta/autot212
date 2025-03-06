import requests
import json


class ScrapeAllocations:
    def __init__(self):
        self.url = "https://api.iris.finance/graphql/"

        self.payload = json.dumps(
            {
                "operationName": "teamsGet",
                "variables": {"input": {"limit": 100, "offset": 0}},
                "query": "query teamsGet($input: TeamsGetInput!) { teamsGet(input: $input) { teams { __typename ...teamFragment } } }  fragment linkFragment on Link { linkKey source linkSource url teamKey description displayName }  fragment teamItemFragment on Team { teamKey title description createdAt companyUrl companyImageUrl deeplinkUrl }  fragment autopilotPortfolioFragment on AutoPilotPortfolio { portfolioKey userKey teamKey portfolioName userFullName userProfileImage portfolioCardImageUrl portfolioCategories pilotSourceDescription tradeDelayTime profileImageLargeUrl assetsUnderManagement description deeplinkUrl pilotSourceDescription pilotStats { totalPilotingCount paidPilotingCount } isDefault userSubtitle holdingsConnection { currentHoldings { symbol name assetDescription pictureUrl percentOfPortfolio assetKey } } stats { portfolioKey risk { score riskAssessment date } performance(input: { includeIntraday: true spans: [ALL_TIME,FIVE_YEAR,THREE_YEAR,ONE_YEAR,YTD,SIX_MONTH,THREE_MONTH,ONE_MONTH,ONE_WEEK] } ) { spanPerformance span } } links { __typename ...linkFragment } createdAt priority }  fragment portfolioFragment on Portfolio { team { __typename ...teamItemFragment } pilotPortfolio { __typename ...autopilotPortfolioFragment } }  fragment teamFragment on Team { teamKey title description createdAt companyUrl companyImageUrl formADVPart2BUrl deeplinkUrl links { __typename ...linkFragment } portfolios { __typename ...portfolioFragment } }",
            }
        )
        self.headers = {
            "user-agent": "okhttp/5.0.0-alpha.14",
            "x-app-version": "1.10.22",
            "accept": "multipart/mixed;deferSpec=20220824, application/graphql-response+json, application/json",
            "coordinate": "1552cfbd-cbea-4eed-8548-5376e5326373",
            "Content-Type": "application/json",
        }

    def get_allocations(self):
        response = requests.request(
            "POST", self.url, headers=self.headers, data=self.payload
        )
        return response.json()
