"""
Task 5: Logistics Intelligence — Analytics API
New file — zero modifications to existing code.
Optimized GROUP BY queries for MINICOM road planning data.
All exports are anonymized (no individual sender names).
"""
from django.db.models import Sum, Count, Avg, F
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from domestic.models import Shipment


# ─────────────────────────────────────────────
# 1. TOP ROUTES — GET /api/analytics/routes/top/
# ─────────────────────────────────────────────
class TopRoutesView(APIView):
    """
    Most frequented origin→destination corridors.
    MINICOM uses this to prioritize road repair budgets.
    Optimized: Single GROUP BY query, no N+1.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        routes = (
            Shipment.objects
            .values('origin', 'destination')
            .annotate(
                total_shipments=Count('id'),
                total_weight_kg=Sum('weight_kg'),
                total_revenue_rwf=Sum('tariff_amount'),
            )
            .order_by('-total_shipments')[:10]
        )

        return Response({
            "report": "Top Traffic Corridors — Rwanda Logistics",
            "unit": "Anonymized aggregate data (no personal identifiers)",
            "routes": [
                {
                    "corridor": f"{r['origin']} → {r['destination']}",
                    "total_shipments": r['total_shipments'],
                    "total_weight_kg": str(r['total_weight_kg']),
                    "total_revenue_rwf": str(r['total_revenue_rwf']),
                }
                for r in routes
            ]
        }, status=status.HTTP_200_OK)


# ─────────────────────────────────────────────
# 2. COMMODITIES — GET /api/analytics/commodities/breakdown/
# ─────────────────────────────────────────────
class CommodityBreakdownView(APIView):
    """
    Cargo volume by shipment type (Domestic vs International).
    Proxy for commodity flow — MINICOM tracks food vs export goods.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        breakdown = (
            Shipment.objects
            .values('shipment_type')
            .annotate(
                count=Count('id'),
                total_weight_kg=Sum('weight_kg'),
                total_revenue_rwf=Sum('tariff_amount'),
                avg_weight_kg=Avg('weight_kg'),
            )
            .order_by('-total_weight_kg')
        )

        total_weight = sum(b['total_weight_kg'] for b in breakdown if b['total_weight_kg'])

        return Response({
            "report": "Cargo Type Breakdown",
            "total_weight_kg": str(total_weight),
            "breakdown": [
                {
                    "type": b['shipment_type'],
                    "shipment_count": b['count'],
                    "total_weight_kg": str(b['total_weight_kg']),
                    "avg_weight_kg": str(round(b['avg_weight_kg'], 2)),
                    "total_revenue_rwf": str(b['total_revenue_rwf']),
                    "share_pct": f"{(b['total_weight_kg'] / total_weight * 100):.1f}%" if total_weight else "0%",
                }
                for b in breakdown
            ]
        }, status=status.HTTP_200_OK)


# ─────────────────────────────────────────────
# 3. REVENUE HEATMAP — GET /api/analytics/revenue/heatmap/
# ─────────────────────────────────────────────
class RevenueHeatmapView(APIView):
    """
    Earnings per origin district — geospatial revenue data.
    Used by finance teams to identify high-value corridors.
    Anonymized: grouped by district, no sender info.
    """
    permission_classes = [IsAuthenticated]

    # Kigali district coordinates for known origins
    DISTRICT_COORDS = {
        "Kigali":  {"lat": -1.9441, "lng": 30.0619},
        "Musanze": {"lat": -1.4990, "lng": 29.6340},
        "Butare":  {"lat": -2.5967, "lng": 29.7394},
        "Gisenyi": {"lat": -1.7022, "lng": 29.2567},
        "Mombasa": {"lat": -4.0435, "lng": 39.6682},
        "Nairobi": {"lat": -1.2921, "lng": 36.8219},
    }

    def get(self, request):
        heatmap = (
            Shipment.objects
            .values('origin')
            .annotate(
                shipment_count=Count('id'),
                total_revenue_rwf=Sum('tariff_amount'),
                total_weight_kg=Sum('weight_kg'),
            )
            .order_by('-total_revenue_rwf')
        )

        return Response({
            "report": "Revenue Heatmap by Origin District",
            "privacy": "Aggregated data only — individual senders not identified",
            "heatmap": [
                {
                    "district": h['origin'],
                    "coordinates": self.DISTRICT_COORDS.get(
                        h['origin'], {"lat": -1.9441, "lng": 30.0619}
                    ),
                    "shipment_count": h['shipment_count'],
                    "total_revenue_rwf": str(h['total_revenue_rwf']),
                    "total_weight_kg": str(h['total_weight_kg']),
                }
                for h in heatmap
            ]
        }, status=status.HTTP_200_OK)


# ─────────────────────────────────────────────
# 4. DRIVER LEADERBOARD — GET /api/analytics/drivers/leaderboard/
# ─────────────────────────────────────────────
class DriverLeaderboardView(APIView):
    """
    Top performing drivers by completed deliveries and cargo moved.
    Anonymized: shows driver ID only, not personal details.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        leaderboard = (
            Shipment.objects
            .filter(driver_assigned__isnull=False)
            .values('driver_assigned')
            .annotate(
                deliveries=Count('id'),
                total_weight_kg=Sum('weight_kg'),
                total_revenue_rwf=Sum('tariff_amount'),
                paid_deliveries=Count(
                    'id', filter=F('payment_status') == 'PAID'
                ),
            )
            .order_by('-deliveries')[:10]
        )

        return Response({
            "report": "Driver Performance Leaderboard",
            "privacy": "Driver IDs only — no personal contact details exposed",
            "leaderboard": [
                {
                    "rank": idx + 1,
                    "driver_id": entry['driver_assigned'],
                    "total_deliveries": entry['deliveries'],
                    "total_weight_kg": str(entry['total_weight_kg']),
                    "total_revenue_rwf": str(entry['total_revenue_rwf']),
                }
                for idx, entry in enumerate(leaderboard)
            ]
        }, status=status.HTTP_200_OK)

