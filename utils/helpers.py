# utils/helpers.py
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, List, Any, Optional

class DataHelper:
    """数据处理辅助类"""
    
    @staticmethod
    def process_attack_results(attack_results: List[Dict]) -> Dict[str, Any]:
        """处理攻击结果数据"""
        if not attack_results:
            return {}
            
        df = pd.DataFrame(attack_results)
        
        return {
            'total': len(attack_results),
            'success_count': len([a for a in attack_results if a.get('success')]),
            'success_rate': (len([a for a in attack_results if a.get('success')]) / len(attack_results) * 100),
            'attack_types': df['vulnerability'].nunique() if 'vulnerability' in df.columns else 0,
            'targets': df['target'].nunique() if 'target' in df.columns else 0,
            'phase_stats': df['phase'].value_counts().to_dict() if 'phase' in df.columns else {}
        }
    
    @staticmethod
    def process_defense_results(defense_results: Dict) -> Dict[str, Any]:
        """处理防御结果数据"""
        if not defense_results:
            return {}
            
        detections = defense_results.get('detections', [])
        responses = defense_results.get('responses', [])
        
        return {
            'total_detections': len(detections),
            'high_risk': len([d for d in detections if d.get('confidence', 0) > 0.8]),
            'total_responses': len(responses),
            'blocked_ips': len(defense_results.get('blocked_ips', []))
        }

class ChartHelper:
    """图表生成辅助类"""
    
    @staticmethod
    def create_attack_chart(attack_results: List[Dict]):
        """创建攻击统计图表"""
        if not attack_results:
            return None
            
        # 攻击类型分布
        type_counts = {}
        for a in attack_results:
            vuln = a.get('vulnerability', 'unknown')
            type_counts[vuln] = type_counts.get(vuln, 0) + 1
        
        if type_counts:
            fig = go.Figure(data=[
                go.Bar(x=list(type_counts.keys()), y=list(type_counts.values()))
            ])
            fig.update_layout(title="攻击类型统计")
            return fig
        return None
    
    @staticmethod
    def create_topology_chart(targets: List[Dict]):
        """创建网络拓扑图"""
        if not targets:
            return None
            
        fig = go.Figure()
        
        for i, target in enumerate(targets):
            # 根据类型设置颜色和图标
            config = {
                'attacker': {'color': 'red', 'symbol': 'triangle-up', 'size': 40},
                'defense': {'color': 'blue', 'symbol': 'shield', 'size': 35},
                'web_server': {'color': 'green', 'symbol': 'circle', 'size': 30},
                'database': {'color': 'orange', 'symbol': 'diamond', 'size': 30}
            }.get(target.get('type', ''), {'color': 'gray', 'symbol': 'circle', 'size': 25})
            
            fig.add_trace(go.Scatter(
                x=[i],
                y=[1],
                mode='markers+text',
                marker=dict(
                    size=config['size'],
                    color=config['color'],
                    symbol=config['symbol'],
                    line=dict(width=2, color='white')
                ),
                text=[target.get('name', 'unknown')],
                textposition="bottom center",
                hoverinfo='text',
                hovertext=f"名称: {target.get('name')}<br>类型: {target.get('type')}<br>IP: {target.get('ip', 'N/A')}"
            ))
        
        # 添加连接线
        for i in range(len(targets)-1):
            fig.add_trace(go.Scatter(
                x=[i, i+1],
                y=[1, 1],
                mode='lines',
                line=dict(color='rgba(100,100,100,0.3)', width=2, dash='dot'),
                hoverinfo='none',
                showlegend=False
            ))
        
        fig.update_layout(
            showlegend=False,
            height=400,
            xaxis=dict(showticklabels=False, showgrid=False, zeroline=False, range=[-0.5, len(targets)-0.5]),
            yaxis=dict(showticklabels=False, showgrid=False, zeroline=False, range=[0.5, 1.5]),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            title="靶场网络拓扑"
        )
        
        return fig