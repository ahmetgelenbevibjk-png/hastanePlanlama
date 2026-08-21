import copy
import random 

from.constraints import can_assign_operation 
from .penalties import calculate_assignment_penalty 
from .constants import (
    DEFAULT_TOTAL_SLOTS,
    DEFAULT_UNASSIGNED_PENALTY,
    ALTERNATIVE_MAX_PENALTY_LIMIT,
    DEFAULT_DAY_NAME,
    DEFAULT_NUM_CANDIDATES,
    GA_POPULATION_SIZE,
    GA_GENERATIONS,
    GA_MUTATION_RATE,
    GA_TOURNAMENT_SIZE,
    GA_ELITISM_RATE,
    
)

class ScheduleOptimizer:
    def __init__(self,total_slots=DEFAULT_TOTAL_SLOTS):
        self.total_slots=total_slots 
        
    def _init_schedules(self,rooms,surgeons,anesthesias):
        room_sched={getattr(r,'id',r):[None] * self.total_slots for r in rooms}
        surgeon_sched = {getattr(s, 'id', s): [None] * self.total_slots for s in surgeons}
        anesthesia_sched = {getattr(a, 'id', a): [None] * self.total_slots for a in anesthesias}
        return room_sched, surgeon_sched, anesthesia_sched 
    
    def _find_best_slot(self,op,rooms,surgeons,anesthesias,day_name,r_sched,s_sched,a_sched):
        
        best_option=None 
        min_penalty =float('inf')
        
        for slot in range(self.total_slots):
            for room in rooms:
                for surgeon in surgeons:
                    for anesthesia in anesthesias:
                        
                        if can_assign_operation(op,surgeon,room,anesthesia, slot,day_name,r_sched,s_sched,a_sched,self.total_slots):
                            
                            penalty = calculate_assignment_penalty(op, surgeon, room, anesthesia, slot, r_sched, s_sched)
                            
                            if penalty < min_penalty:
                                min_penalty=penalty 
                                best_option=(slot,room,surgeon,anesthesia,penalty)
                                if penalty==0:
                                    return best_option 
                                
        return best_option if best_option else (None,None,None,None,None)
    
    
    def _assign_to_sched(self, op, slot, room, surgeon, anesthesia, r_sched, s_sched, a_sched):
        r_id = getattr(room, 'id', room)
        s_id = getattr(surgeon, 'id', surgeon)
        a_id = getattr(anesthesia, 'id', anesthesia)
        duration = getattr(op, 'duration_slot', 1)
        
        for offset in range(duration):
            curr_slot=slot + offset 
            if curr_slot < self.total_slots:
                r_sched[r_id][curr_slot] = op.id
                s_sched[s_id][curr_slot] = op.id
                a_sched[a_id][curr_slot] = op.id
                
                
    def _decode_chromosome(self, chromosome, rooms, surgeons, anesthesias, day_name):
        r_sched, s_sched, a_sched = self._init_schedules(rooms, surgeons, anesthesias)
        assigned, unassigned = [], []
        
        for op in chromosome: 
            slot,room,surgeon,anesthesia,penalty =self._find_best_slot(
                op,rooms,surgeons,anesthesias,day_name,r_sched,s_sched,a_sched
            )
            if slot is not None:
                self._assign_to_sched(op,slot,room,surgeon,anesthesia,r_sched,s_sched,a_sched)
                assigned.append({
                    'operation':op,'start_slot':slot,'room':room,
                    'surgeon':surgeon,'anesthesia':anesthesia,'penalty':penalty 
                })
            else: 
                unassigned.append(op)
                
        total_penalty = sum(x['penalty'] for x in assigned) + (len(unassigned) * DEFAULT_UNASSIGNED_PENALTY)
        
        fitness = max(0.0, float(ALTERNATIVE_MAX_PENALTY_LIMIT - total_penalty))
        
        return {
            'chromosome':chromosome,
            'fitness_score':round(fitness,2),
            'total_penalty':total_penalty,
            'assigned':assigned,
            'unassigned':unassigned,
            'schedules': {'room':r_sched,'surgeon':s_sched , 'anesthesia':a_sched}
        }
        
    def _select_parent(self,population):
        
        candidates=random.sample(population,min(len(population),GA_TOURNAMENT_SIZE))
        candidates.sort(key=lambda x: x['fitness_score'], reverse=True)
        return candidates[0]['chromosome']

    def _crossover(self, parent1, parent2):
        size = len(parent1)
        if size < 2:
            return copy.deepcopy(parent1)

        cx1, cx2 = sorted(random.sample(range(size), 2))
        child = [None] * size
        child[cx1:cx2 + 1] = parent1[cx1:cx2 + 1]

        p1_set = set(parent1[cx1:cx2 + 1])
        p2_remaining = [item for item in parent2 if item not in p1_set]

        idx = 0
        for i in range(size):
            if child[i] is None:
                child[i] = p2_remaining[idx]
                idx += 1
        return child

    def _mutate(self, chromosome):
        mutated = copy.deepcopy(chromosome)
        if random.random() < GA_MUTATION_RATE and len(mutated) > 1:
            idx1, idx2 = random.sample(range(len(mutated)), 2)
            mutated[idx1], mutated[idx2] = mutated[idx2], mutated[idx1]
        return mutated
    
    def optimize_with_alternatives( self,operations,rooms,surgeons,anesthesias, day_name=DEFAULT_DAY_NAME, num_candidates=DEFAULT_NUM_CANDIDATES ):
        if not operations:
            return {'best_plan':None,'all_candidates':[]}
        
        population= []
        
        p_sorted = sorted(operations, key=lambda x: getattr(x, 'priority', ''), reverse=True)
        d_sorted = sorted(operations, key=lambda x: getattr(x, 'duration_slot', 1), reverse=True)
        population.extend([p_sorted, d_sorted])
        
        while len(population) < GA_POPULATION_SIZE:
            shuffled=copy.deepcopy(operations)
            random.shuffle(shuffled)
            population.append(shuffled)
            
        evaluated = [
            self._decode_chromosome(chrom,rooms,surgeons,anesthesias,day_name)
            for chrom in population
        ]
        
        for _ in range(GA_GENERATIONS):
            evaluated.sort(key=lambda x: x['fitness_score'],reverse=True)
            new_chroms=[]
            
            elitism_count=max(1,int(GA_POPULATION_SIZE * GA_ELITISM_RATE))
            for i in range(elitism_count):
                new_chroms.append(copy.deepcopy(evaluated[i]['chromosome']))
                
            while len(new_chroms)< GA_POPULATION_SIZE:
                p1=self._select_parent(evaluated)
                p2=self._select_parent(evaluated)
                child=self._crossover(p1,p2)
                child=self._mutate(child)
                new_chroms.append(child)
                
            evaluated =[
                self._decode_chromosome(chrom,rooms,surgeons,anesthesias,day_name)
                for chrom in new_chroms 
            ]
            
        evaluated.sort(key=lambda x: x['fitness_score'], reverse=True)
        candidates,seen_fingerprints= [],set()
        
        for ind in evaluated:
            fingerprint=tuple(sorted([
                (item['operation'].id,item['start_slot'],getattr(item['room'],'id',item['room']))
                for item in ind['assigned']
            ]))
            
            if fingerprint in seen_fingerprints:
                continue 
            seen_fingerprints.add(fingerprint)
            
            penalties_breakdown=[
                {
                    'reason': f"{getattr(item['operation'], 'operation_name', item['operation'].id)} ceza puanı",
                    'points': round(item['penalty'], 2)
                }
                for item in ind['assigned'] if item['penalty']>0
            ]
            
            candidate ={
                'candidate_id':len(candidates) + 1,
                'strategy_name':f"Genetik Evrimleşmiş Plan #{len(candidates) +1}",
                'fitness_score': ind['fitness_score'],
                'total_penalty':ind['total_penalty'],
                'penalties':penalties_breakdown,
                'assigned_count': len(ind['assigned']),
                'unassigned_count': len(ind['unassigned']),
                'assigned': ind['assigned'],
                'unassigned': ind['unassigned'],
                'schedules': ind['schedules']
            }
            candidates.append(candidate)
            
            if len(candidates)>= num_candidates:
                break 
            
        return {
            'best_plan':candidates[0]if candidates else None,
            'all_candidates':candidates 
        }