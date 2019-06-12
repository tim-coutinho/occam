/*
 * Copyright © 1990 The Portland State University OCCAM Project Team
 * [This program is licensed under the GPL version 3 or later.]
 * Please see the file LICENSE in the source
 * distribution of this software for license terms.
 */

#ifndef ___VariableBasedManager
#define ___VariableBasedManager

#include "ManagerBase.h"

/**
 * ManagerBase - implements base functionality of an ocManager.  This class is the
 * provider for algorithms which manipulate core objects.  The class is extensible,
 * to allow new managers to be developed for different analysis approaches.
 *
 * The base manager has default implementions for commonly required operations, such as:
 * - generation of descendent models from an existing model
 * - creation of a table for a model, by projection from an input table
 * - creation of a fit table for a model using IPF
 * - calculation of various parameters for a table or model
 * - determination if a model contains loops
 */
class VBMManager: public ManagerBase {
public:
    //-- create an ManagerBase object, supplying it with a variable list and a table
    //-- of input data.  Typically an application will read the input data and variable
    //-- definitions, and then construct the appropriate manager.
    VBMManager(VariableList *vars, Table *input);
    VBMManager();

    // initialize an ManagerBase object, reading in standard options and data files.
    bool initFromCommandLine(int argc, char **argv);

    //-- delete this object
    virtual ~VBMManager();

    //-- return all the child relations of the given relation.  The children array
    //-- must have been preallocated, of size at least the number of variables in
    //-- the relation (this is the number of children). Projections are created, if
    //-- indicated
    void makeAllChildRelations(Relation *rel, Relation **children, bool makeProject = false);

    //-- make a child model of a given model, by removing a relation and then adding back
    //-- in all its children
    Model *makeChildModel(Model *model, int remove, bool* fromCache = 0, bool makeProject =
            false);

    //-- make the top and bottom reference models, given a relation which represents
    //-- the saturated model. This function also sets the default reference model based
    //-- on whether the system is directed or undirected.
    void makeReferenceModels(Relation *top);

    //-- return top, bottom, or default reference
    Model *getTopRefModel() {
        return topRef;
    }
    Model *getBottomRefModel() {
        return bottomRef;
    }
    Model *getRefModel() {
        return refModel;
    }

    //-- set ref model
    Model *setRefModel(const char *name);

    //-- compute various measures. These generally involve the top and/or bottom
    //-- reference models, so makeReferenceModels must be called before any of
    //-- these are used.
    double computeExplainedInformation(Model *model);
    double computeUnexplainedInformation(Model *model);
    double computeDDF(Model *model);
    void setDDFMethod(int method);

    void setUseInverseNotation(int flag);
    int getUseInverseNotation() {
        return useInverseNotation;
    }

    //-- flag to indicate whether to make projections on all relations
    void setMakeProjection(bool proj) {
        projection = proj;
    }
    bool makeProjection() {
        return projection;
    }

    bool makeProjection(Table *t1, Table *t2, Relation *rel) {
        return ManagerBase::makeProjection(t1, t2, rel);
    }

    //-- get/set search object
    class SearchBase *getSearch() {
        return search;
    }
    void setSearch(const char *name);

    //-- compute basic informational statistics
    void computeInformationStatistics(Model *model);

    //-- compute DF and related statistics
    void computeDFStatistics(Model *model);

    //-- compute log likelihood statistics
    void computeL2Statistics(Model *model);

    //-- compute Pearson statistics
    void computePearsonStatistics(Model *model);

    //-- compute dependent variable statistics
    void computeDependentStatistics(Model *model);

    //-- compute BP-based transmission
    //void doBPIntersection(Model *model);
    double computeBPT(Model *model);

    //-- compute all statistics based on BP_T
    void computeBPStatistics(Model *model);

    //-- compute percentage correct of a model for a directed system
    void computePercentCorrect(Model *model);

    //-- Filter definitions. If a filter is set on a search object, then
    //-- generated models which do not pass the filter are not kept.
    enum RelOp {
        LESSTHAN, EQUALS, GREATERTHAN
    };
    void setFilter(const char *attrname, double attrvalue, RelOp op);
    virtual bool applyFilter(Model *model);

    //-- Sort definitions
    void setSortAttr(const char *name);
    const char *getSortAttr() {
        return sortAttr;
    }
    void setDirectionection(int dir) {
        sortDirection = dir;
    }
    int getDirectionection() {
        return sortDirection;
    }

    //-- Single model reports. For multi-model reports see Report.h
    void printFitReport(Model *model, FILE *fd);

    void printBasicStatistics();

    //-- Get predicting variables, for a model of adependent system.
    //-- The predicting variables are those in any relation other than
    //-- the IV relation. Optionally the dependent variables can be included in this.
    //-- the varindices arg is filled with the variable indices;
    //-- it needs to have been allocated large enough.

    void calculateBP_AicBic(Model *model);

private:
    // data
    bool projection;
    class SearchBase *search;
    char *filterAttr;
    double filterValue;
    char *sortAttr;
    int sortDirection;
    RelOp filterOp;
    int useInverseNotation;

    bool firstCome;
    bool firstComeBP;
    double refer_AIC;
    double refer_BIC;
    double refer_BP_AIC;
    double refer_BP_BIC;

    // Called by computeDDF to build a list of the relations that differ between two models.
    void buildDDF(Relation *rel, Model *loModel, Model *diffModel, bool directed);
    int DDFMethod; // method to use for computing DDF. 0=new (default); 1=old
};

#endif

