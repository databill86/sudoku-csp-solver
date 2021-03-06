#!/usr/bin/env python
# CSP-problem class by Ilse van der Linden & Sander van Dorsten

""" Module that has the ability for users model a Constraint Satisfaction Problem.


"""
from pprint import pprint
import time
from collections import namedtuple
from copy import deepcopy

Statistics = namedtuple("Statistics", " runtime, backtracks, splits")

class Problem(object):
    """ An instance of a CSP problem

    TODO: fill in the different methods of the class. I've added them but have not yet implemented them because I wanted to work on the program structure first.

    """
    def __init__(self, minimal_remaining_values = False, forward_checking = False ):
        """
        @param solver: Problem solver used to find solutions
                       (default is BacktrackingSolver)
        @type solver:  instance of a Solver subclass
        """
        self.forward_checking = forward_checking
        self.mrv = minimal_remaining_values

        self.solver = BacktrackingSolver(forward_checking=self.forward_checking, minimal_remaining_values=self.mrv)
        self.constraints = []
        self.variables = {}
        self.var_constr_dict = {}

        #statistical values
        self.runtime = 0
        self.splits = 0 
        self.backtracks = 0

    def addConstraint(self, constraintID, constrained_variables=None):
        """ Add a constraint over the variables to the problem

        @param constraint: an instance of one of the constraint classes,
                           defines a constraint over the variables given
        @type  constraint: an instance of one of the constrain classes
        @param  variables: a list of variables over which the constraint
                           works. Default is all variables.
        @type   variables: a list
        """
        if constraintID == 1:
            constraint = AllDifferentConstraint(self.variables, constrained_variables)
            self.constraints.append(constraint)
        pass

    def addVariable(self, variable, domain):
        """ Add a single variable to the Problem with a given domain

        @param variable: variable that we add to our problem variables
        @type variable:  some single value, for example a string, an int. In the sudoku case, it's a tuple.
        @param domain: Domain of the added variable
        @type domain:  instance of Domain, a list

        TODO: add exception and error handling.
        """
        self.variables[variable] = domain

    def addVariables(self, variables, domain):
        """ Add multiple variables to the problem with the same given domain

        @param variables: variable that we add to our problem variables
        @type variables:  something we can iterate over, a list, a range.
        @param domain: Domain of the added variable
        @type domain:  instance of Domain, a list
        """
        for variable in variables:
            self.addVariable(variable, domain)

    def mapVarToConstraints(self):
        """ Based on variables and constraint list make dictionary that
        maps variables to their constraints
        """
        #var_constr_dict = {}

        for variable in self.variables:
            self.var_constr_dict[variable] = []

        for constraint_obj in self.constraints:
            for key in constraint_obj._constrained_variables:
                # add the constraint object itself to the list of constraints for that variable
                self.var_constr_dict[key].append(constraint_obj)
        return self.var_constr_dict

    def getSolution(self):
        """
        Returns a solution for the CSP-problem

        @rtype: ?

        """
        """ HEURISTIEK OPTIES
        1. most constrained variable
        2. smallest domain variable
        3. mix of 1 and 2
        MORE IDEAS? 

        deze implementeren we later in een andere solver die we SuperSolver() of iets dergelijks noemen. BacktrackingSolver() is een naive implementatie.
        """
        start = time.time()
        self.var_constr_dict = self.mapVarToConstraints()

        solution = self.solver.getSolution(self)
        self.runtime = time.time() - start
        # solution is a instance of problem, where variables is all done!
        return solution, self.getStatistics()

    def getStatistics(self):
        stats = Statistics(runtime = self.runtime, backtracks = self.backtracks, splits = self.splits)
        return stats


class Variable(object):
    domain = [] # domein van de variabele. 
    constraints = [] # lijst met constraints over deze variabele
    value = (0,0) # tuple coresponding to the coordinates of the variable.


class Solver(object):
    pass

class BacktrackingSolver(Solver):
    """ simple solver that uses backtracking.

    example

     _ 9 4 _ _ _ 1 3 _ 
     _ _ _ _ _ _ _ _ _ 
     _ _ _ _ 7 6 _ _ 2
     _ 8 _ _ 1 _ _ _ _ 
     _ 3 2 _ _ _ _ _ _ 
     _ _ _ 2 _ _ _ 6 _ 
     _ _ _ _ 5 _ 4 _ _ 
     _ _ _ _ _ 8 _ _ 7
     _ _ 6 3 _ 4 _ _ 8

    Steps:
    1. kies volgens een heuristiek een leeg vakje (bijvoorbeeld (1, 1))
        2. kies volgens een heuristiek een assignment (bijvoorbeeld '1')
        check de constraints waar de variabele in voorkomt. True? --> ga naar 1, False? --> verwijder de assignment (in het voorbeeld '1') uit het mogelijke domein en ga naar 2.
        Als het domein leeg is, ga terug naar het voorgaande leeg vakje en ga naar stap 2.

    Volgens mij is dit een OK naive implementatie?

    """

    def __init__(self, forward_checking = True, minimal_remaining_values = True):
        self.forward_checking = forward_checking
        self.mrv = minimal_remaining_values
        self.backtracks = 0


    def getSolution(self, problem):
        """ we updaten eerst alle domains
            daarna gaan we stapje voor stapje unassigned variables assignen. als dit fout gaat, kiezen we een andere variable.

            maak een snapshot van het probleem
            voor variabelen in het snapshot:
                als variabele unassigned is:
                    kies een assignment uit het domein
                        check alle3 de constraints of ze voldoen.
                        True --> volgende variabele
                        False --> kies een andere assignment
                    Geen assignments meer over? ga terug naar het vorige keuzemoment (snapshot)
        """
        #if self.forward_checking:
        problem, assigned = self.update_domains(problem,[])

        return self.backtrack(problem)

    def backtrack(self, problem):

        # find unassigned variables
        u = (v for v in problem.variables if len(problem.variables[v]) > 1 )
        unassigned_vars = [ (len(problem.variables[v]), v) for v in u ]

        if len(unassigned_vars) == 0:
            return problem.variables

        # order unassigned variables
        if self.mrv:
            unassigned_vars.sort()
        unassigned = unassigned_vars[0][1]

        copy_variables = deepcopy(problem.variables)      
        
        # Get domain of unassigned variable
        domain = problem.variables[unassigned]
        for value in domain:
            # Assign value to variable
            problem.variables[unassigned] = [value]
            # Update domains
            problem, assigned = self.update_domains(problem, [unassigned])
            if self.check_assignment(problem, assigned):
                #stack.append(deepcopy(new_state))
                #print len(stack)
                problem.splits += 1
                result = self.backtrack(problem)
                if isinstance(result, dict):
                    return result
            problem.variables = deepcopy(copy_variables)
        st = time.time()
        problem.variables = deepcopy(copy_variables)
        rt = time.time() - st
        problem.backtracks += 1
        return False

    def check_assignment(self, problem, assigned):
        for variable in assigned:
            for constraint in problem.var_constr_dict[variable]:
                for var in constraint._constrained_variables[variable]:
                    if len(problem.variables[var]) == 1:
                        #print problem.variables[variable][0], problem.variables[var][0]
                        if problem.variables[variable][0] == problem.variables[var][0]:
                            #print variable, var
                            #print problem.variables[variable], problem.variables[var]
                            return False
        return True 

    def update_domains(self, problem, assigned):
        """ we krijgen hier een probleem, waar variabelen al een assignment kunnen hebben. voor bovenstaande voorbeeldsudoku zou het volgende dus gelden:
        problem.variables = {
                                (1,1) : [3]
                                (1,2) : [9]
                                (1,3) : [1,2,3,4,5,6,7,8,9]
                                  .
                                  .
                                  .
                                (9,9) : [1,2,3,4,5,6,7,8,9]
                            }
        Voordat we ook maar iets gaan invullen (dus bvb (1,3) --> '2'), gaan we domain reduction doen. we willen dat bij (1,3) het domein niet [1:9] wordt, maar [2,5]. dit komt omdat, volgens alle constraints (Row, Column, en Box) dit de enige waarde zijn die dit hokje nog kan aannemen.

        HOE DOEN WE DIT?
        REPEAT UNTIL NO UPDATES ANY MORE
        voor elke var (x,y):
            voor elke constraint, horende bij (x,y) (bvb (1,3):
                voor elke var in dit constraint horende bij (x,y):
                    als _constrained_variables[(a,b)] heeft lengte 1 (is dus assigned):
                        verwijder deze mogelijkheid voor (x,y) uit zijn domein.

        """

        # For first update round: find all assigned values
        if len(assigned) == 0:
            assigned = [ v for v in problem.variables if len(problem.variables[v]) == 1 ]
        # Loop over assigned variables    
        for var1 in assigned:
            # Find constraints for assigned var
            for constraint in problem.var_constr_dict[var1]:
                # Find variables that assigned var is constrained by
                for var2 in constraint._constrained_variables[var1]:
                    # If variables that assigned var is constrained by
                    # have its assigned value in domain, remove it
                    if len(problem.variables[var2]) != 1:
                        assigned_value = problem.variables[var1][0]
                        if assigned_value in problem.variables[var2]:
                            problem.variables[var2].remove(assigned_value)
                            if len(problem.variables[var2]) == 1:
                                assigned.append(var2)
        return problem, assigned


class AllDifferentConstraint(object):
    """ init a constraint over variables. If these variables are not given, the constraint will be over all variables.
    """

    # '_' shows that it's a internal variable.
    _constrained_variables = {}

    def __init__(self, variables, constrained_variables):
        """ init a constraint. 
            
            @param constrained_variables: variables over which the constraint is. the default is all variables
            @type constrained_variables: a list. for example [11,12,13]
        """
        self._constrained_variables = {}
        for var1 in constrained_variables:
            # add var to _constrained_variables
            self._constrained_variables[var1] = []
            # now we add all OTHER variables from constrained_variables as value of the dict entry. so first entry would be: (1,1) : [(1,2),(1,3), (1,4)....., (1,9)]
            for var2 in constrained_variables:
                if var2 != var1:
                    self._constrained_variables[var1].append(var2)
        #pprint(self._constrained_variables)

    def check(self, problem, updated_var):
        """ check if constraint is still satisfied, after an update. 
            TODO: this is going to be something like: given a snapshot! not yet implemnted though.

            stel je assigned: (1,2) --> '1'. dan moet je alle constraints die iets zeggen over (1,2) checken, of de waarde 1 daar wel kan. (1,3) mag dus niet al '1' zijn.

            voor alle andere variabelen die worden ge-effect door het constraint:
                    als deze variabelen assigned zijn, en hetzelfde zijn als de updated_var, kan de updated_var niet die waarde krijgen. 
        """
        for var2 in self._constrained_variables[updated_var]:
            if len(problem.variables[var2]) == 1:
                if problem.variabels[var2] == problem.variabels[updated_var]:
                    return False
        return True


